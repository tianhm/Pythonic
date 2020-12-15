/*
 * This file is part of Pythonic.

 * Pythonic is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * Pythonic is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with Pythonic. If not, see <https://www.gnu.org/licenses/>
 */

#ifndef ELEMENTEDITOR_H
#define ELEMENTEDITOR_H

#include <QDialog>
#include <QWidget>
#include <QCheckBox>
#include <QLineEdit>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QJsonObject>
#include <QJsonArray>
#include <QLabel>
#include <QFont>
#include <QComboBox>
#include <QVariant>
#include <QRegExp>
#include <QRegExpValidator>
#include <QList>
#include "baselabel.h"

#define ID_FONTSIZE 12



namespace ElementEditorTypes {

    struct Rule {
        QString         dependence;
        QList<QString>  dependentValues;
    };

    enum Type {
        QComboBox,
        QLineEdit,
        NoType
    };

}


class Elementeditor : public QDialog
{
    Q_OBJECT
public:
    explicit Elementeditor(quint32 id, QWidget *parent = nullptr);

    //! Indicates if the element specific input elements are already loaded
    bool     m_editorSetup{false};

signals:

    void updateConfig(const QJsonObject config);

public slots:

    void openEditor(const QJsonObject config);
    void loadEditorConfig(const QJsonArray config);
    void accept() override;

private:

    static ElementEditorTypes::Type hashType(QString const &inString);

    void            genConfig();

    void            checkRules();

    void            addRules(const QJsonArray rules);

    void            addComboBox(QJsonObject &dropDownJSON);

    void            addLineEdit(QJsonObject &lineeditJSON);

    QHBoxLayout     m_mainLayout;

    QWidget         m_generalConfig;
    QWidget         m_specificConfig;

    QVBoxLayout     m_generalCfgLayout;
    QVBoxLayout     m_specificCfgLayout;

    QLabel          m_id;

    QLineEdit       m_objectName;

    QCheckBox       m_toggleLogging;
    QCheckBox       m_toggleDebug;
    QCheckBox       m_toggleMP;

    QPushButton     m_saveButton;

    QList<ElementEditorTypes::Rule> m_rules;

    const static QLoggingCategory logC;

};

#endif // ELEMENTEDITOR_H
