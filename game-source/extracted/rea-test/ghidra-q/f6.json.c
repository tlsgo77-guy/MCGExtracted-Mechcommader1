
/* public virtual void __thiscall Camera::render(void) 
   public: virtual void __thiscall Camera::render(void) */

void __thiscall Camera::render(Camera *this)

{
  int *piVar1;
  int iVar2;
  float fVar3;
  short sVar4;
  short sVar5;
  undefined4 *puVar6;
  int iVar7;
  uint uVar8;
  ulong uVar9;
  long lVar10;
  bool bVar11;
  float10 fVar12;
  long lVar13;
  long lVar14;
  File local_ec [76];
  float local_a0;
  float local_9c;
  float local_98;
  float local_94;
  float local_90;
  float local_8c;
  _pane *local_88;
  _window *local_84;
  undefined4 local_80;
  undefined4 local_7c;
  undefined4 local_78;
  undefined4 local_74;
  undefined4 local_70;
  undefined4 local_6c;
  int local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  int local_50;
  int local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  int local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  char *local_10;
  int local_c;
  char *local_8;
  
                    /* START-> L:\mcx\Camera\Camera.cpp: ? */
  MaxObjectsDrawn = 0;
  piVar1 = *(int **)(this + 0xdc);
  local_88 = globalPane;
  local_84 = globalWindow;
  if (piVar1 != (int *)0x0) {
    globalPane = (_pane *)(**(code **)(*piVar1 + 0x24))();
    puVar6 = (undefined4 *)(**(code **)(*piVar1 + 0x24))();
    globalWindow = (_window *)*puVar6;
  }
  prepareBackground(this);
  fVar3 = (float)(*(int *)(globalPane + 0xc) - *(int *)(globalPane + 4));
  if ((fVar3 != *(float *)(this + 0x14)) ||
     ((float)(*(int *)(globalPane + 0x10) - *(int *)(globalPane + 8)) != *(float *)(this + 0x18))) {
    iVar7 = *(int *)(globalPane + 0x10);
    iVar2 = *(int *)(globalPane + 8);
    *(float *)(this + 0x14) = fVar3;
    *(float *)(this + 0x18) = (float)(iVar7 - iVar2);
    fVar12 = (float10)fsin((float10)*(float *)(this + 8) * (float10)0.0174532925199);
    *(float *)(this + 0xc) = (float)fVar12;
    fVar12 = (float10)fcos((float10)*(float *)(this + 8) * (float10)0.0174532925199);
    *(float *)(this + 0x10) = (float)fVar12;
    *(float *)(this + 0x1c) = fVar3 * 0.5;
    *(float *)(this + 0x20) = (float)(iVar7 - iVar2) * 0.5;
  }
  local_c = *(int *)(this + 0xe0);
  bVar11 = local_c != 1;
  if ((uint)bVar11 != lastZoom) {
    SpriteManager::dumpALL(spriteManager);
  }
  lastZoom = (uint)bVar11;
  ElementPool::reset();
  ElementBuffer::reset(ElementList);
  (**(code **)(**(int **)(this + 0xb8) + 4))(*(undefined4 *)(this + 0x4c),1);
  if (drawTerrainGrid != 0) {
    Terrain::drawLines(land);
  }
  CraterManager::render(craterManager);
  ObjectQueue::render(objectList);
  if (gRestartRender != 0) {
    gRestartRender = 0;
    ElementPool::reset();
    ElementBuffer::reset(ElementList);
    CraterManager::render(craterManager);
    ObjectQueue::render(objectList);
  }
  ElementBuffer::sort(ElementList);
  ElementBuffer::draw(ElementList);
  if (drawCameraCircle != 0) {
    piVar1 = *(int **)(*(int *)(this + 0xdc) + 0x4dc);
    if (piVar1 == (int *)0x0) {
      local_10 = (char *)0x0;
      local_14 = 0.0;
    }
    else {
      iVar7 = (**(code **)(*piVar1 + 0x3c))();
      local_8 = (char *)(*(int *)(*(int *)(this + 0xdc) + 0x4f0) - iVar7);
      local_c = (**(code **)(*piVar1 + 0x38))();
      local_c = *(int *)(*(int *)(this + 0xdc) + 0x4ec) - local_c;
      local_14 = (float)local_c;
      local_10 = (char *)(float)(int)local_8;
    }
    inverseProject(this,(vector_2d *)&local_14,(vector_3d *)&local_a0);
    local_c = *(int *)(this + 0xe0);
    local_1c = *(float *)(this + 0xc0);
    local_18 = *(float *)(this + 0xc4);
    if (local_c == 1) {
      local_8 = (char *)0x3f000000;
    }
    else {
      local_8 = (char *)0x3f800000;
    }
    local_94 = local_a0 - *(float *)(this + 0xbc);
    local_90 = local_9c - local_1c;
    local_8c = local_98 - local_18;
    FUN_006015e0();
    local_14 = local_20 * (float)local_8 * *(float *)(this + 0x10) +
               local_1c * (float)local_8 * *(float *)(this + 0x10) + *(float *)(this + 0x1c);
    local_10 = (char *)(((local_20 * (float)local_8 * *(float *)(this + 0xc) +
                         *(float *)(this + 0x20)) -
                        local_1c * (float)local_8 * *(float *)(this + 0xc)) -
                       local_18 * (float)local_8);
    local_8 = local_10;
    _floor((double)local_14);
    sVar4 = __ftol();
    lVar14 = 0xfe;
    lVar10 = 3;
    lVar13 = 3;
    _floor((double)(float)local_8);
    sVar5 = __ftol();
    AG_ellipse_fill(globalPane,(int)sVar4,(int)sVar5,lVar13,lVar10,lVar14);
  }
  if (gamePaused != 0) {
    Palette::getHazePalette(gamePalette,-7);
    local_80 = 0;
    local_7c = 0;
    local_78 = 0;
    local_74 = 0;
    local_70 = 0;
    local_6c = 0;
    local_68 = (**(code **)(*(int *)application + 0xc))();
    local_68 = local_68 + -1;
    local_64 = 0;
    local_60 = 0;
    local_5c = 0;
    local_58 = 0;
    local_54 = 0;
    local_50 = (**(code **)(*(int *)application + 0xc))();
    local_50 = local_50 + -1;
    local_4c = (**(code **)(*(int *)application + 0x10))();
    local_4c = local_4c + -1;
    local_48 = 0;
    local_44 = 0;
    local_40 = 0;
    local_3c = 0;
    local_38 = 0;
    local_34 = (**(code **)(*(int *)application + 0x10))();
    local_34 = local_34 + -1;
    local_30 = 0;
    local_2c = 0;
    local_28 = 0;
    local_24 = 0;
    aPort::frame(screenPort);
    _VFX_translate_polygon();
    if (pauseShape == (uchar *)0x0) {
      local_8 = (char *)0x0;
      FullPathFileName::init((FullPathFileName *)&local_8,(char *)&artPath,s_pause,s__shp);
      File::File(local_ec);
      uVar8 = File::open(local_ec,local_8,1,0x32);
      Assert((uint)(uVar8 == 0),uVar8,s__Could_not_find_Pause_Shape_,(char *)0x0);
      uVar9 = File::fileSize(local_ec);
      pauseShape = UserHeap::malloc(ObjectTypeManager::objectCache,uVar9);
      File::read(local_ec,pauseShape,uVar9);
      File::close(local_ec);
      File::~File(local_ec);
      FullPathFileName::~FullPathFileName((FullPathFileName *)&local_8);
    }
    lVar10 = 0x3c;
    lVar13 = __ftol();
    AG_shape_draw(globalPane,pauseShape,0,lVar13,lVar10);
  }
  if (gameAsked != 0) {
    Palette::getHazePalette(gamePalette,-7);
    local_80 = 0;
    local_7c = 0;
    local_78 = 0;
    local_74 = 0;
    local_70 = 0;
    local_6c = 0;
    local_68 = (**(code **)(*(int *)application + 0xc))();
    local_68 = local_68 + -1;
    local_64 = 0;
    local_60 = 0;
    local_5c = 0;
    local_58 = 0;
    local_54 = 0;
    local_50 = (**(code **)(*(int *)application + 0xc))();
    local_50 = local_50 + -1;
    local_4c = (**(code **)(*(int *)application + 0x10))();
    local_4c = local_4c + -1;
    local_48 = 0;
    local_44 = 0;
    local_40 = 0;
    local_3c = 0;
    local_38 = 0;
    local_34 = (**(code **)(*(int *)application + 0x10))();
    local_34 = local_34 + -1;
    local_30 = 0;
    local_2c = 0;
    local_28 = 0;
    local_24 = 0;
    aPort::frame(screenPort);
    _VFX_translate_polygon();
    if (DAT_007f0934 == (uchar *)0x0) {
      local_8 = (char *)0x0;
      FullPathFileName::init((FullPathFileName *)&local_8,(char *)&artPath,s_asked,s__shp);
      File::File(local_ec);
      uVar8 = File::open(local_ec,local_8,1,0x32);
      Assert((uint)(uVar8 == 0),uVar8,s__Could_not_find_Asked_Shape_,(char *)0x0);
      uVar9 = File::fileSize(local_ec);
      DAT_007f0934 = UserHeap::malloc(ObjectTypeManager::objectCache,uVar9);
      File::read(local_ec,DAT_007f0934,uVar9);
      File::close(local_ec);
      File::~File(local_ec);
      FullPathFileName::~FullPathFileName((FullPathFileName *)&local_8);
    }
    lVar13 = __ftol();
    lVar10 = __ftol();
    AG_shape_draw(globalPane,DAT_007f0934,0,lVar10,lVar13);
  }
  if (*(int *)(this + 0xdc) != 0) {
    globalPane = local_88;
    globalWindow = local_84;
  }
  if (local_c != 1) {
    currentScaleFactor = 1.0;
    return;
  }
  currentScaleFactor = 0.5;
                    /* END-> L:\mcx\Camera\Camera.cpp: ? */
  return;
}

