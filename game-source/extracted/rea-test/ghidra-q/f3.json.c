
/* public virtual long __thiscall Camera::init(class FitIniFile *,
                                               int,
                                               long) 
   public: virtual long __thiscall Camera::init(class FitIniFile *,int,long) */

long __thiscall Camera::init(Camera *this,FitIniFile *param_1,int param_2,long param_3)

{
  Camera *pCVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  _pane *p_Var5;
  FitIniFile *this_00;
  long lVar6;
  aTitleWindow *this_01;
  aEmptyTitleWindow *this_02;
  int iVar7;
  float10 fVar8;
  long lStack_18;
  ulong local_14;
  ulong local_10;
  ulong local_c;
  ulong local_8;
  
                    /* START-> L:\mcx\Camera\Camera.cpp: ? */
  this_00 = param_1;
  if ((scaleTable == (uchar *)0x0) && (lVar6 = buildScaleTable(this), lVar6 != 0)) {
    return lVar6;
  }
  lVar6 = FitIniFile::readIdFloat(param_1,s_PixelScalar,(float *)(this + 4));
  if ((((((lVar6 == 0) &&
         (lVar6 = FitIniFile::readIdFloat(param_1,s_ProjectionAngle,(float *)(this + 8)), lVar6 == 0
         )) && (lVar6 = FitIniFile::readIdFloat(param_1,s_PositionX,(float *)(this + 0xbc)),
               lVar6 == 0)) &&
       ((lVar6 = FitIniFile::readIdFloat(param_1,s_PositionY,(float *)(this + 0xc0)), lVar6 == 0 &&
        (lVar6 = FitIniFile::readIdFloat(param_1,s_PositionZ,(float *)(this + 0xc4)), lVar6 == 0))))
      && ((lVar6 = FitIniFile::readIdUChar(param_1,s_BackgroundColor,(uchar *)(this + 0x48)),
          lVar6 == 0 &&
          ((lVar6 = FitIniFile::readIdUChar(param_1,s_Ready,(uchar *)(this + 0xd4)), lVar6 == 0 &&
           (lVar6 = FitIniFile::readIdLong(param_1,s_HazeLevel,(long *)(this + 0x4c)), lVar6 == 0)))
          ))) &&
     ((lVar6 = FitIniFile::readIdLong(param_1,s_HazeInc,(long *)(this + 0x50)), lVar6 == 0 &&
      (lVar6 = FitIniFile::readIdLong(param_1,s_CameraScale,(long *)(this + 0xe0)), lVar6 == 0)))) {
    lVar6 = FitIniFile::readIdULong(param_1,s_WindowLeft,&local_10);
    p_Var5 = globalPane;
    if (lVar6 == 0) {
      lVar6 = FitIniFile::readIdULong(param_1,s_WindowTop,&local_8);
      if (lVar6 != 0) {
        return lVar6;
      }
      lVar6 = FitIniFile::readIdULong(param_1,s_WindowRight_00793ff0,&local_c);
      if (lVar6 != 0) {
        return lVar6;
      }
      lVar6 = FitIniFile::readIdULong(param_1,s_WindowBottom,&local_14);
      if (lVar6 != 0) {
        return lVar6;
      }
      lVar6 = FitIniFile::readIdLong(param_1,s_MainWindow_00793fd4,&lStack_18);
      if (lVar6 == 0) {
        *(long *)(this + 0x58) = lStack_18;
      }
      else {
        *(undefined4 *)(this + 0x58) = 0;
      }
      this_01 = aObject::operator_new(0x500);
      if (this_01 == (aTitleWindow *)0x0) {
        this_01 = (aTitleWindow *)0x0;
      }
      else {
        aTitleWindow::aTitleWindow(this_01);
        *(undefined ***)this_01 = &viewWindow::_vftable_;
      }
      *(aTitleWindow **)(this + 0xdc) = this_01;
      if (this_01 == (aTitleWindow *)0x0) {
        return -0x303fffe;
      }
      if (*(int *)(this + 0x58) == 0) {
        this_02 = aObject::operator_new(0x4d4);
        if (this_02 == (aEmptyTitleWindow *)0x0) {
          return -0x303fffe;
        }
        param_1 = (FitIniFile *)aEmptyTitleWindow::aEmptyTitleWindow(this_02);
        if (param_1 == (FitIniFile *)0x0) {
          return -0x303fffe;
        }
        iVar7 = (**(code **)(*(int *)param_1 + 4))
                          (local_10,local_8,local_c - local_10,local_14 - local_8,0);
        if (iVar7 != 0) {
          return iVar7;
        }
        if (*(aTitleBar **)(param_1 + 0x4d0) != (aTitleBar *)0x0) {
          aTitleBar::showZoomButton(*(aTitleBar **)(param_1 + 0x4d0),1);
        }
        if (*(int **)(param_1 + 0x4cc) != (int *)0x0) {
          (**(code **)(**(int **)(param_1 + 0x4cc) + 0xfc))(1);
        }
        if (*(aTitleBar **)(param_1 + 0x4d0) != (aTitleBar *)0x0) {
          aTitleBar::showCloseButton(*(aTitleBar **)(param_1 + 0x4d0),1);
        }
      }
      else if (mainHolder == (aMainWindow *)0x0) {
        param_1 = aObject::operator_new(0x4c8);
        if (param_1 == (FitIniFile *)0x0) {
          mainHolder = (aMainWindow *)0x0;
          return -0x303fffe;
        }
        aObject::aObject((aObject *)param_1);
        mainHolder = (aMainWindow *)param_1;
        *(undefined ***)param_1 = &aMainWindow::_vftable_;
        lVar6 = aMainWindow::init((aMainWindow *)param_1);
        if (lVar6 != 0) {
          return lVar6;
        }
      }
      iVar7 = (**(code **)(*(int *)this_01 + 4))
                        (local_10,local_8,local_c - local_10,local_14 - local_8,0);
      if (iVar7 != 0) {
        return iVar7;
      }
      iVar7 = *(int *)(this + 0x58);
      *(undefined2 *)(this_01 + 0x58) = 4;
      if (iVar7 == 0) {
        (**(code **)(*(int *)param_1 + 0x148))(this_01);
        (**(code **)(*(int *)this_01 + 0x1c))(0,0,0);
      }
      else {
        if (this[0xd4] != (Camera)0x0) {
          (**(code **)(*(int *)mainHolder + 0x148))(this_01);
        }
        *(undefined4 *)(this_01 + 0x4d4) = 1;
        *(undefined2 *)(this_01 + 0x58) = 4;
      }
      *(long *)(this + 0xd0) = param_3;
      viewWindow::setWindowCamera((viewWindow *)this_01,this);
      lStack_18 = 0;
      *(float *)(this + 0x14) = (float)(local_c - local_10);
      *(float *)(this + 0x18) = (float)(local_14 - local_8);
      fVar8 = (float10)fsin((float10)*(float *)(this + 8) * (float10)0.0174532925199);
      *(float *)(this + 0xc) = (float)fVar8;
      fVar8 = (float10)fcos((float10)*(float *)(this + 8) * (float10)0.0174532925199);
      *(float *)(this + 0x10) = (float)fVar8;
      *(float *)(this + 0x1c) = (float)((float10)(local_c - local_10) * (float10)0.5);
      *(float *)(this + 0x20) = (float)(local_14 - local_8) * 0.5;
    }
    else {
      *(undefined4 *)(this + 0xdc) = 0;
      iVar7 = *(int *)(p_Var5 + 0xc);
      iVar2 = *(int *)(p_Var5 + 4);
      iVar3 = *(int *)(p_Var5 + 0x10);
      iVar4 = *(int *)(p_Var5 + 8);
      *(float *)(this + 0x14) = (float)(iVar7 - iVar2);
      *(float *)(this + 0x18) = (float)(iVar3 - iVar4);
      fVar8 = (float10)fsin((float10)*(float *)(this + 8) * (float10)0.0174532925199);
      *(float *)(this + 0xc) = (float)fVar8;
      fVar8 = (float10)fcos((float10)*(float *)(this + 8) * (float10)0.0174532925199);
      *(float *)(this + 0x10) = (float)fVar8;
      *(float *)(this + 0x1c) = (float)(iVar7 - iVar2) * 0.5;
      *(float *)(this + 0x20) = (float)(iVar3 - iVar4) * 0.5;
    }
    if (param_2 == 0) {
      *(undefined4 *)(this + 0x44) = 0;
      *(undefined4 *)(this + 0xe8) = 0;
      lVar6 = 0;
    }
    else {
      lVar6 = FitIniFile::readIdLong(this_00,s_ObjectClassId,(long *)(this + 100));
      if ((lVar6 == 0) &&
         (lVar6 = FitIniFile::readIdLong(this_00,s_partNumber,(long *)(this + 0x60)), lVar6 == 0)) {
        lVar6 = FitIniFile::readIdLong(this_00,s_SwoopyCamOff,&leaveSwoopyOff);
        if (lVar6 != 0) {
          leaveSwoopyOff = 0;
        }
        lVar6 = FitIniFile::readIdLong(this_00,s_ScrollyCam,(long *)(this + 0xec));
        if (lVar6 != 0) {
          *(long *)(this + 0xec) = 0;
        }
        pCVar1 = this + 0xf8;
        lVar6 = FitIniFile::readIdFloat(this_00,s_DistanceThreshold,(float *)pCVar1);
        if (lVar6 != 0) {
          *(undefined1 **)pCVar1 = &DAT_41200000;
        }
        lVar6 = FitIniFile::readIdFloat(this_00,s_MinScrollSpeed,(float *)(this + 0xfc));
        if (lVar6 != 0) {
          *(float *)pCVar1 = 90.0;
        }
        lVar6 = FitIniFile::readIdFloat(this_00,s_SpeedFactor,(float *)(this + 0xf4));
        if (lVar6 != 0) {
          *(float *)(this + 0xf4) = 50.0;
        }
        lVar6 = FitIniFile::readIdFloat(this_00,s_CamDistance,(float *)(this + 0xa8));
        if (lVar6 != 0) {
          *(float *)(this + 0xa8) = 50.0;
        }
        lVar6 = FitIniFile::readIdFloat(this_00,s_DistanceFactor,(float *)(this + 0xb4));
        if (lVar6 != 0) {
          *(undefined1 **)(this + 0xb4) = &DAT_41c80000;
        }
        lVar6 = FitIniFile::readIdFloat(this_00,s_CamSpeed,(float *)(this + 0xa4));
        if (lVar6 != 0) {
          *(float *)(this + 0xa4) = 50.0;
        }
        lVar6 = FitIniFile::readIdFloat(this_00,s_JumpThreshold,(float *)(this + 0xa0));
        if (lVar6 != 0) {
          *(undefined1 **)(this + 0xa0) = &DAT_437a0000;
        }
        *(undefined4 *)(this + 0x44) = 1;
        *(undefined4 *)(this + 0xe8) = 0;
        return 0;
      }
    }
  }
  return lVar6;
}

