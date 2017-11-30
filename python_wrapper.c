//----------------------------------------------------------------------------------
// main.cpp
//
// Intan Technoloies RHD2000 Rhythm Interface API
// Version 1.2 (23 September 2013)
//
// Copyright (c) 2013 Intan Technologies LLC
//
// This software is provided 'as-is', without any express or implied warranty.
// In no event will the authors be held liable for any damages arising from the
// use of this software.
//
// Permission is granted to anyone to use this software for any applications that
// use Intan Technologies integrated circuits, and to alter it and redistribute it
// freely.
//
// See http://www.intantech.com for documentation and product information.
//----------------------------------------------------------------------------------

// #include <QtCore> // used for Qt applications
#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <time.h>

using namespace std;

#include "rhd2000evalboard.h"
#include "rhd2000registers.h"
#include "rhd2000datablock.h"
#include "okFrontPanelDLL.h"

extern "C" {
    Rhd2000EvalBoard* EvalBoard_new(){ return new Rhd2000EvalBoard(); } 
    void EvalBoard_open(Rhd2000EvalBoard* b){ b->open();  }
}
