import sys, logging, pickle, datetime, os, signal, time, itertools, tty, termios, select
import json
import multiprocessing as mp
import eventlet, json
from eventlet import wsgi, websocket, greenthread
from threading import Timer, Thread, Event
from pathlib import Path
from zipfile import ZipFile
from enum import Enum
from execution_operator import Operator
from stdin_reader import stdinReader
from screen import reset_screen
from configio import ToolboxLoader, ConfigLoader, EditorLoader, ConfigWriter
import operator
from PySide2.QtCore import QCoreApplication, QObject, QThread, Qt, QTimer
from PySide2.QtCore import Signal


class LogLvl(Enum):
    DEBUG       = 0
    INFO        = 1
    WARNING     = 2
    CRITICAL    = 3
    FATAL       = 4





@websocket.WebSocketWSGI
def rcv(ws):


    def send(command):
        #logging.debug('testfunc called')
        ws.send(json.dumps(command))
    
    ws.environ['mainWorker'].frontendCtrl.connect(send)
    bConnected = True
    while bConnected:
        greenthread.sleep(0.3)
        QCoreApplication.processEvents()
        try:
            jsonHeartBeat = {   "cmd": "Heartbeat",
                                "address" : {"target" : "MainWindow"}}
            #next(self.spinner)
            ws.send(json.dumps(jsonHeartBeat))
        except Exception as e:
            logging.info('PythonicWeb - RCV Socket connection lost: {}'.format(e))
            ws.environ['mainWorker'].frontendCtrl.disconnect(send)
            bConnected = False

    logging.debug('PythonicWeb - RCV Socket closed')




@websocket.WebSocketWSGI
def ctrl(ws):
    logging.debug('PythonicDaemon - CTRL WebSocket connected')   
    while True:
        m = ws.wait()
        if m is None:
            logging.debug('PythonicDaemon - CTRL Socket Closed')            
            break;   
        else:
            msg = json.loads(m)
            
            logging.debug('PythonicWeb    - Command: {}'.format(msg['cmd']))

            if msg['cmd'] == 'logMsg':
                # logging
                logObj = msg['data']

                if logObj['logLvL'] == LogLvl.DEBUG.value:
                    logging.debug('PythonicWeb    - {}'.format(logObj['msg']))
                if logObj['logLvL'] == LogLvl.DEBUG.value:
                    logging.debug('PythonicWeb    - {}'.format(logObj['msg']))
                elif logObj['logLvL'] == LogLvl.INFO.value:
                    logging.info('PythonicWeb    - {}'.format(logObj['msg']))
                elif logObj['logLvL'] == LogLvl.WARNING.value:
                    logging.warning('PythonicWeb    - {}'.format(logObj['msg']))
                elif logObj['logLvL'] == LogLvl.CRITICAL.value:
                    logging.error('PythonicWeb    - {}'.format(logObj['msg']))
                elif logObj['logLvL'] == LogLvl.FATAL.value:
                    logging.critical('PythonicWeb    - {}'.format(logObj['msg']))

            elif msg['cmd'] == 'start':
                logging.debug('PythonicWeb    - {}'.format("START"))

            elif msg['cmd'] == 'writeConfig':
                logging.debug('Config loaded')
                # Save config to to memory
                ws.environ['mainWorker'].gridConfig = msg['data']
                # Save config to file
                ws.environ['mainWorker'].saveConfig.emit(msg['data'])
            elif msg['cmd'] == 'StartExec':
                elementId = msg['data']        
                ws.environ['mainWorker'].startExec.emit(elementId, ws.environ['mainWorker'].gridConfig)
            elif msg['cmd'] == 'StopExec':
                elementId = msg['data']
                logging.debug('PythonicWeb    - {}'.format(msg['cmd']))
            elif msg['cmd'] == 'QueryConfig':
                logging.debug('PythonicWeb    - {}'.format(msg['cmd']))
                ws.environ['mainWorker'].loadConfig()
            elif msg['cmd'] == 'QueryToolbox':
                logging.debug('PythonicWeb    - {}'.format(msg['cmd']))
                ws.environ['mainWorker'].loadTools()
            elif msg['cmd'] == 'QueryEditorToolbox' :
                logging.debug('PythonicWeb    - {}'.format(msg['cmd']))
                addr        = msg['address']
                typeName    = msg['data']
                ws.environ['mainWorker'].loadEditorConfig(addr, typeName)

                #data  = msg['']




def dispatch(environ, start_response):

    """
        WEBSOCKETS
    """

    root_url        = 'PythonicWeb/'
    root_static      = 'PythonicWeb/static/'


    png_req4 = environ['PATH_INFO'][-4:] # last 4 characters '.png'
    png_req3 = environ['PATH_INFO'][-3:] # last 4 characters '.js'

    if environ['PATH_INFO'] == '/ctrl':
        logging.debug('PythonicDaemon - Open CTRL WebSocket')     
        return ctrl(environ, start_response)
    elif environ['PATH_INFO'] == '/rcv':
        logging.debug('PythonicDaemon - Open RCV WebSocket')     
        return rcv(environ, start_response)


        """
            STANDARD HTML ENDPOINTS
        """

    elif environ['PATH_INFO'] == '/':
        #logging.debug('PATH_INFO == \'/\'')
        
        start_response('200 OK', [  ('content-type', 'text/html'),
                                    ('Cross-Origin-Opener-Policy', 'same-origin'),
                                    ('Cross-Origin-Embedder-Policy', 'require-corp')])
        return [open(os.path.join(os.path.dirname(__file__),
            root_url + 'templates/PythonicWeb.html')).read()]


    elif environ['PATH_INFO'] == '/qtlogo.svg':
        #logging.debug('PATH_INFO == \'/qtlogo.svg\'')

        open_path = os.path.join(os.path.dirname(__file__),root_url + 'static/qtlogo.svg')

        with open(open_path,'rb') as f:
            img_data = f.read()

        start_response('200 OK', [('content-type', 'image/svg+xml'),
                                ('content-length', str(len(img_data)))])

        return [img_data]

    # IMAGES (*.png)
    elif png_req4 == '.png':
        #logging.debug('PATH_INFO == ' + environ['PATH_INFO'])
        
        open_path = os.path.join(os.path.dirname(__file__), root_static + environ['PATH_INFO'])

        with open(open_path,'rb') as f:
            img_data = f.read()
        
        start_response('200 OK', [('content-type', 'image/png'),
                                ('content-length', str(len(img_data)))])
        
        return [img_data]

    # JAVS SCRIPT (*.js)

    elif png_req3 == '.js':
        #logging.debug('PATH_INFO == ' + environ['PATH_INFO'])
        open_path = os.path.join(os.path.dirname(__file__), root_static + environ['PATH_INFO'])
        with open(open_path,'rb') as f:
            img_data = f.read()

        
        start_response('200 OK', [('content-type', 'application/javascript')])
        
        return [img_data]

    elif environ['PATH_INFO'] == '/PythonicWeb.wasm':
        #logging.debug('PATH_INFO == \'/PythonicWeb.wasm\'')

        open_path = os.path.join(os.path.dirname(__file__), root_url + 'static/PythonicWeb.wasm')

        with open(open_path,'rb') as f:
            bin_data = f.read()

        start_response('200 OK', [('content-type', 'application/wasm')])
        return [bin_data]		

    else:
        path_info = environ['PATH_INFO']
        logging.debug('PATH_INFO = {}'.format(path_info))
        return None


class WSGI_Server(QThread):

    def __init__(self, mainWorker):
        super().__init__()
        self.mainWorker = { 'mainWorker' : mainWorker }

    def run(self):

        listener = eventlet.listen(('127.0.0.1', 7000))
        wsgi.server(listener, dispatch, log_output=False, environ=self.mainWorker)




class MainWorker(QObject):

    kill_all        = Signal()
    update_logdate  = Signal(object)
    log_level       = logging.DEBUG
    formatter       = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

    max_grid_size   = 50
    max_grid_cnt    = 5
    gridConfig      = None


    startExec       = Signal(object, object)
    saveConfig      = Signal(object)
    frontendCtrl    = Signal(object)

    def __init__(self, app):
        super(MainWorker, self).__init__()
        self.app = app
        mp.set_start_method('spawn')

        # Instantiate WSGI Server
        self.wsgi_server = WSGI_Server(self)
        
        # Instantiate Standard Input Reader
        self.stdinReader = stdinReader()
        self.stdinReader.print_procs.connect(self.printProcessList)
        self.stdinReader.quit_app.connect(self.exitApp)

        # Instantiate Execution Operator
        self.operator = Operator()
        self.startExec.connect(self.operator.startExec)
        self.startExec.connect(self.saveConfig)
        
        # Instantiate ToolboxLoader
        self.toolbox_loader = ToolboxLoader()
        self.toolbox_loader.tooldataLoaded.connect(self.forwardCmd)
        
        # Instantiate (Element)-EditorLoader

        self.editor_loader = EditorLoader()
        self.editor_loader.editorLoaded.connect(self.forwardCmd)
        
        # Instantiate ConfigWriter
        self.config_writer = ConfigWriter()
        self.config_writer.configSaved.connect(self.forwardCmd)
        self.saveConfig.connect(self.config_writer.saveConfig)

        # Instantiate ConfigLoader
        self.config_loader = ConfigLoader()
        self.config_loader.tooldataLoaded.connect(self.forwardCmd)
        
        self.update_logdate.connect(self.stdinReader.updateLogDate)
        
        self.fd = sys.stdin.fileno()
        if os.isatty(sys.stdin.fileno()):
            self.orig_tty_settings = termios.tcgetattr(self.fd) 

        self.logger = logging.getLogger()
        self.logger.setLevel(self.log_level)
        self.log_date = datetime.datetime.now()

        log_date_str = self.log_date.strftime('%Y_%m_%d')
        month = self.log_date.strftime('%b')
        year = self.log_date.strftime('%Y')
        home_dict = str(Path.home())
        file_path = '{}/PythonicDaemon_{}/{}/log_{}.txt'.format(home_dict, year, month, log_date_str) 
        self.ensure_file_path(file_path)

        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.formatter)

        self.logger.addHandler(file_handler)
        self.update_logdate.emit(log_date_str) # forward log_date_str to instance of stdinReader


        logging.debug('MainWorker::__init__() called')

    def exitApp(self):
        print('# Stopping all processes....')
        self.kill_all.emit()
        time.sleep(3) # wait for 1 seconds to kill all processes
        self.app.quit()
        os.kill(self.app.applicationPid(), signal.SIGTERM) # kill all related threads


    def ensure_file_path(self, file_path):

        directory = os.path.dirname(file_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

    
    def printProcessList(self):
        b_proc_found = False
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.orig_tty_settings)
        reset_screen()

        print('# BAUSTELLE')

        print('\n')
        tty.setraw(sys.stdin.fileno()) 
    
    def update_logfile(self):

        now = datetime.datetime.now().date()
        if (now != self.log_date.date()):
            self.logger.removeHandler(self.logger.handlers[0])
            log_date_str = now.strftime('%Y_%m_%d')
            month = now.strftime('%b')
            year = now.strftime('%Y')
            home_dict = str(Path.home())
            file_path = '{}/PythonicDaemon_{}/{}/log_{}.txt'.format(home_dict, year, month, log_date_str) 
            self.ensure_file_path(file_path)
            file_handler = logging.FileHandler(file_path)
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            self.log_date = datetime.datetime.now()
            self.update_logdate.emit(log_date_str)

    def start(self, args):

        #print('\n Arguments: {}'.format(args))
        reset_screen()        
        # first argument is main_console.py
        # second argument is script location

        logging.debug('MainWorker::start() called')
        #logging.debug('MainWorker::start() Open the following file: {}'.format(grid_file))


        self.stdinReader.start() # call run() method in separate thread
        self.wsgi_server.start()
        self.operator.start()


    def on_callback(self):

        self.stdinReader.run()
    

    def loadTools(self):
        
        logging.debug('MainWorker::loadTools() called')
        self.toolbox_loader.start()

    def loadEditorConfig(self, address, typeName):
        
        logging.debug('MainWorker::loadEditorConfig() called')
        self.editor_loader.startLoad(address, typeName)

    def forwardCmd(self, cmd):

        logging.debug('MainWorker::forwardCmd() called')
        self.frontendCtrl.emit(cmd)

    def loadConfig(self):

        logging.debug('MainWorker::loadConfig() called')
        self.config_loader.start()
           

    def checkArgs(self, args):

        b_file_found = False
        grid_file = None

        for argument in args:
            if argument[0] == '-' or argument[0] == '--':
                print('Option found: {}'.format(argument))
            else:
                if not b_file_found:
                    b_file_found = True
                    grid_file = argument

        return grid_file
