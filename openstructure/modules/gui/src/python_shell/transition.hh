//------------------------------------------------------------------------------
// This file is part of the OpenStructure project <www.openstructure.org>
//
// Copyright (C) 2008-2020 by the OpenStructure authors
//
// This library is free software; you can redistribute it and/or modify it under
// the terms of the GNU Lesser General Public License as published by the Free
// Software Foundation; either version 3.0 of the License, or (at your option)
// any later version.
// This library is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
// details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this library; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
//------------------------------------------------------------------------------

#ifndef PYTHON_SHELL_TRANSITION_HH
#define PYTHON_SHELL_TRANSITION_HH

#include <ost/gui/python_shell/python_interpreter.hh>
#include "transition_guard.hh"
#include <utility>

#include <QObject>
#include <QEvent>
//fw decl
class QKeyEvent;
class QMouseEvent;

namespace ost { namespace gui {

//fw decl
class State;
class PythonShellWidget;
class ShellHistory;

class TransitionBase: public QObject{
Q_OBJECT
public:
  TransitionBase(State* target, TransitionGuard* guard=new TransitionGuard());
signals:
  void triggered();
protected:
  void trigger_();
  bool is_active_();
  State* target_;
  TransitionGuard* guard_;
};

class AutomaticTransition: public TransitionBase{
Q_OBJECT
public:
  AutomaticTransition(State* target, TransitionGuard* guard=new TransitionGuard());
  bool checkTransition();
};

class SignalTransition: public TransitionBase{
Q_OBJECT
public:
  SignalTransition(QObject * sender,const char *  signal, State* target, TransitionGuard* guard=new TransitionGuard());
protected slots:
  void onSignal();
};

class KeyEventTransition: public TransitionBase{
Q_OBJECT
public:
  KeyEventTransition(int key,Qt::KeyboardModifiers modifiers, State* target, bool swallow_event=true, TransitionGuard* guard=new TransitionGuard());
  virtual std::pair<bool,bool> checkEvent(QKeyEvent* event);
protected:
  int key_;
  Qt::KeyboardModifiers modifiers_;
  bool swallow_;
};

class MouseEventTransition: public TransitionBase{
Q_OBJECT
public:
  MouseEventTransition(QEvent::Type type,Qt::MouseButton button,Qt::KeyboardModifiers modifiers, State* target, bool swallow_event=true, TransitionGuard* guard=new TransitionGuard());
  virtual std::pair<bool,bool> checkEvent(QMouseEvent* event);
protected:
  QEvent::Type type_;
  Qt::MouseButton button_;
  Qt::KeyboardModifiers modifiers_;
  bool swallow_;
};




}}//ns
#endif // PYTHON_SHELL_TRANSITION_HH
