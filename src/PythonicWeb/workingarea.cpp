#include "workingarea.h"


Q_LOGGING_CATEGORY(log_workingarea, "WorkingArea")


WorkingArea::WorkingArea(QWidget *parent)
    : QFrame(parent)
{
    setAcceptDrops(true);
    setObjectName("workBackground");
    setStyleSheet("#workBackground { background-color: \
                  qlineargradient(x1:0 y1:0, x2:1 y2:1, stop:0 #366a97, stop: 0.5 silver, stop:1 #ffc634)}");

    m_mastergridLayout.addLayout(&m_gridLayout, 0, 0, Qt::AlignCenter);

    setLayout(&m_mastergridLayout);
    show();

    qCDebug(log_workingarea, "called");
}
