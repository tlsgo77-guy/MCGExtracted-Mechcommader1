
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* public long __thiscall aSystem::startupDirectDraw(long,
                                                     long,
                                                     long) 
   public: long __thiscall aSystem::startupDirectDraw(long,long,long) */

long __thiscall aSystem::startupDirectDraw(aSystem *this,long param_1,long param_2,long param_3)

{
  aSystem *paVar1;
  aSystem *paVar2;
  int *piVar3;
  undefined4 uVar4;
  long lVar5;
  HWND hWnd;
  aSystem *paVar6;
  uint uVar7;
  undefined1 uVar8;
  int iVar9;
  BMI *pBVar10;
  LOGICALPALETTE *pLVar11;
  undefined4 *puVar12;
  bool bVar13;
  undefined4 local_378 [95];
  undefined4 local_1fc [95];
  undefined4 local_80 [5];
  int local_6c;
  undefined4 local_18;
  HWND local_14;
  aSystem *local_10;
  aSystem *local_c;
  aSystem *local_8;
  
  paVar1 = this + 0x4b0;
  paVar2 = this + 0x4ac;
  *(undefined4 *)paVar1 = 0;
  *(undefined4 *)paVar2 = 0;
  local_8 = paVar2;
  uVar7 = _DirectDrawCreate_12(0,paVar1,0);
  if ((uVar7 != 0) ||
     (uVar7 = (**(code **)**(undefined4 **)paVar1)(*(undefined4 **)paVar1,&_IID_IDirectDraw2,paVar2)
     , uVar7 != 0)) {
    Fatal(uVar7,s_Cannot_initialize_DirectDraw_,(char *)0x0);
  }
  piVar3 = *(int **)paVar2;
  puVar12 = local_378;
  for (iVar9 = 0x5f; iVar9 != 0; iVar9 = iVar9 + -1) {
    *puVar12 = 0;
    puVar12 = puVar12 + 1;
  }
  puVar12 = local_1fc;
  for (iVar9 = 0x5f; iVar9 != 0; iVar9 = iVar9 + -1) {
    *puVar12 = 0;
    puVar12 = puVar12 + 1;
  }
  local_378[0] = 0x17c;
  local_1fc[0] = 0x17c;
  (**(code **)(*piVar3 + 0x2c))(piVar3,local_378,local_1fc);
  pBVar10 = &bmi;
  for (iVar9 = 10; iVar9 != 0; iVar9 = iVar9 + -1) {
    *(undefined4 *)pBVar10 = 0;
    pBVar10 = pBVar10 + 4;
  }
  DAT_007a9f94 = param_1;
  _DAT_007a9fa0 = 0;
  _bmi = 0x28;
  pLVar11 = &LogicalPalette;
  for (iVar9 = 0x101; iVar9 != 0; iVar9 = iVar9 + -1) {
    *(undefined4 *)pLVar11 = 0;
    pLVar11 = pLVar11 + 4;
  }
  local_14 = *(HWND *)(this + 0x90c);
  _DAT_007a9f9c = 1;
  _DAT_007a9f98 = -param_2;
  _DAT_007a9f9e = 8;
  _LogicalPalette = 0x300;
  _DAT_007aa3c2 = 0x100;
  DesktopDC = GetDC(local_14);
  GetSystemPaletteEntries(DesktopDC,0,0x100,(LPPALETTEENTRY)&DAT_007aa3c4);
  iVar9 = 0;
  do {
    (&DAT_007a9fba)[iVar9] = (&DAT_007aa3c4)[iVar9];
    (&DAT_007a9fb9)[iVar9] = (&DAT_007aa3c5)[iVar9];
    (&DAT_007a9fb8)[iVar9] = (&DAT_007aa3c6)[iVar9];
    (&DAT_007a9fbb)[iVar9] = 0;
    if ((iVar9 < 0x25) || (0x3d7 < iVar9)) {
      uVar8 = 0;
    }
    else {
      uVar8 = 1;
    }
    (&DAT_007aa3c7)[iVar9] = uVar8;
    iVar9 = iVar9 + 4;
  } while (iVar9 != 0x400);
  hPalette = CreatePalette((LOGPALETTE *)&LogicalPalette);
  holdpalette = SelectPalette(DesktopDC,hPalette,0);
  RealizePalette(DesktopDC);
  OffScreenBufferDC = CreateCompatibleDC(DesktopDC);
  OffScreenhDIBSection =
       CreateDIBSection(OffScreenBufferDC,(BITMAPINFO *)&bmi,0,(void **)&DAT_007ab104,(HANDLE)0x0,0)
  ;
  OffScreenhOldBitmap = SelectObject(OffScreenBufferDC,OffScreenhDIBSection);
  SetStretchBltMode(OffScreenBufferDC,3);
  hWnd = local_14;
  paVar1 = this + 0x4b4;
  *(undefined4 *)paVar1 = 0;
  local_10 = this + 0x4b8;
  local_c = this + 0x4c0;
  *(undefined4 *)local_10 = 0;
  bVar13 = gFullScreen != 0;
  gWidth = param_1;
  gHeight = param_2;
  DAT_007ab0d4 = 0;
  *(undefined4 *)local_c = 0;
  if (bVar13) {
    uVar7 = (**(code **)(*piVar3 + 0x50))(piVar3,local_14,0x13);
    if (uVar7 != 0) {
      Fatal(uVar7,s__Unable_to_Set_Exclusive_Mode_,(char *)0x0);
    }
    ShowWindow(hWnd,5);
    lVar5 = param_2;
    uVar7 = (**(code **)(*piVar3 + 0x54))(piVar3,param_1,param_2,param_3,0,0);
    while (uVar7 == 0x8876021c) {
      uVar7 = (**(code **)(*piVar3 + 0x54))(piVar3,param_1,lVar5,param_3,0,0);
    }
    if (uVar7 != 0) {
      Fatal(uVar7,s__Unable_to_Set_Display_Mode_,(char *)0x0);
    }
    puVar12 = local_80;
    for (iVar9 = 0x1b; iVar9 != 0; iVar9 = iVar9 + -1) {
      *puVar12 = 0;
      puVar12 = puVar12 + 1;
    }
    local_80[0] = 0x6c;
    local_80[1] = 0x21;
    local_18 = 0x4218;
    local_6c = 2;
    iVar9 = (**(code **)(*piVar3 + 0x18))(piVar3,local_80,paVar1,0);
    paVar2 = local_8;
    if (iVar9 != 0) {
      local_6c = 1;
      iVar9 = (**(code **)(**(int **)local_8 + 0x18))(*(int **)local_8,local_80,paVar1,0);
      if (iVar9 != 0) {
        local_80[1] = 1;
        local_18 = 0x4200;
        local_6c = 0;
        iVar9 = (**(code **)(**(int **)paVar2 + 0x18))(*(int **)paVar2,local_80,paVar1,0);
        if (iVar9 != 0) {
          local_18 = 0x200;
          uVar7 = (**(code **)(**(int **)paVar2 + 0x18))(*(int **)paVar2,local_80,paVar1,0);
          if (uVar7 != 0) {
            Fatal(uVar7,s_Unable_to_Create_Primary_Surface_0078a0e8,(char *)0x0);
          }
        }
      }
    }
    DAT_007ab0d4 = local_6c;
    if (local_6c != 0) {
      param_2 = 4;
      (**(code **)(**(int **)paVar1 + 0x30))(*(int **)paVar1,&param_2,local_10);
    }
    paVar6 = local_c;
    if (param_3 != 8) {
      DAT_007ab108 = 1;
      return 0;
    }
    uVar7 = (**(code **)(**(int **)paVar2 + 0x14))(*(int **)paVar2,4,&DAT_007aa3c4,local_c,0);
    if (uVar7 != 0) {
      Fatal(uVar7,s__Unable_to_Create_Primary_Palett,(char *)0x0);
    }
    piVar3 = *(int **)paVar1;
    uVar4 = *(undefined4 *)paVar6;
    uVar7 = (**(code **)(*piVar3 + 0x7c))(piVar3,uVar4);
    if (uVar7 == 0x887601c2) {
      (**(code **)(*piVar3 + 0x6c))(piVar3);
      uVar7 = (**(code **)(*piVar3 + 0x7c))(piVar3,uVar4);
    }
    if (uVar7 != 0) {
      Fatal(uVar7,s__Unable_to_Attach_Palette_to_Pri,(char *)0x0);
    }
  }
  DAT_007ab108 = 1;
  return 0;
}

