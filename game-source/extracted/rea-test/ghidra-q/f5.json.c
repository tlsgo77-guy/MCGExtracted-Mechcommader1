
/* public virtual long __thiscall Camera::update(void) 
   public: virtual long __thiscall Camera::update(void) */

long __thiscall Camera::update(Camera *this)

{
  vector_2d *pvVar1;
  int *piVar2;
  float *pfVar3;
  frame_of_ref *pfVar4;
  int iVar5;
  vector_3d *pvVar6;
  undefined4 uVar7;
  float10 fVar8;
  float10 fVar9;
  float fVar10;
  vector_3d *in_stack_fffffebc;
  vector_2d *pvVar11;
  undefined1 local_12c [36];
  vector_3d local_108 [12];
  undefined1 local_fc [12];
  vector_3d local_f0 [12];
  undefined1 local_e4 [12];
  vector_3d local_d8 [12];
  undefined4 local_cc;
  undefined4 local_c8;
  undefined4 local_c4;
  float local_c0;
  float local_bc;
  float local_b8;
  float local_b4;
  float local_b0;
  float local_ac;
  frame_of_ref local_a8 [12];
  float local_9c;
  float local_98;
  float local_94;
  undefined4 local_84;
  undefined4 local_80;
  undefined4 local_7c;
  float local_78;
  float local_74;
  float local_70;
  float local_6c;
  float local_68;
  float local_64;
  float local_60;
  float local_5c;
  float local_58;
  float local_54;
  float local_50;
  float local_4c;
  float local_48;
  float local_44;
  float local_40;
  float local_3c;
  float local_38;
  float local_34;
  float local_30;
  float local_2c;
  float local_28;
  float local_24;
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  float local_8;
  
  local_1c = *(float *)(this + 0xbc);
  local_18 = *(float *)(this + 0xc0);
  local_14 = *(float *)(this + 0xc4);
  if (*(int *)(this + 0x44) == 0) goto LAB_006af339;
  if (*(int *)(this + 0x44) != 1) {
    return -1;
  }
  piVar2 = *(int **)(this + 0x5c);
  if (piVar2 == (int *)0x0) goto LAB_006af339;
  pfVar3 = (float *)(**(code **)(*piVar2 + 0x6c))(local_fc);
  local_38 = *pfVar3;
  local_34 = pfVar3[1];
  local_30 = pfVar3[2];
  pfVar4 = (frame_of_ref *)(**(code **)(*piVar2 + 0xac))(local_12c);
  frame_of_ref::operator=(local_a8,pfVar4);
  pfVar3 = (float *)(**(code **)(*piVar2 + 0xa0))(local_e4);
  local_28 = pfVar3[1];
  local_2c = *pfVar3;
  local_24 = pfVar3[2];
  local_3c = 0.0;
  iVar5 = (**(code **)(*piVar2 + 400))();
  if (iVar5 == 0) {
    (**(code **)(*(int *)this + 0x20))(0,0);
    return 0;
  }
  if (piVar2[1] == 2) {
    local_3c = (float)piVar2[0x238];
  }
  fVar8 = ((float10)local_3c + (float10)45.0) * (float10)0.0174532925199;
  fVar9 = (float10)fsin(fVar8);
  local_20 = (float)fVar9;
  fVar8 = (float10)fcos(fVar8);
  local_3c = (float)fVar8;
  FUN_006015e0(local_a8);
  operator*((vector_3d *)&local_84,&local_9c);
  pvVar6 = (vector_3d *)operator*((vector_3d *)&local_48,(float *)local_a8);
  uVar7 = operator+(local_d8,pvVar6);
  FUN_0063df10(uVar7);
  operator*(local_d8,&local_78);
  pvVar6 = (vector_3d *)operator*((vector_3d *)&local_84,&local_9c);
  in_stack_fffffebc = (vector_3d *)&local_48;
  uVar7 = operator-(in_stack_fffffebc,pvVar6);
  FUN_0063df10(uVar7);
  iVar5 = *(int *)(this + 0xac);
  if (iVar5 == 0) {
LAB_006aee3a:
    if ((*(int *)(this + 0xb0) == 0) &&
       ((*(int *)(this + 0xe4) != 0 ||
        ((*(int *)(this + 0xec) != 0 && (*(int *)(this + 0xf0) != 0)))))) {
      if ((*(int *)(this + 0xec) == 0) || (*(int *)(this + 0xf0) == 0)) {
        if (((*(int *)(this + 0xe4) != 0) &&
            (SQRT(local_28 * local_28 + local_24 * local_24 + local_2c * local_2c) != 0.0)) ||
           (*(int *)(this + 0xe8) == 0)) {
          if (((*(float *)(this + 0x78) != local_9c) || (*(float *)(this + 0x7c) != local_98)) ||
             (*(float *)(this + 0x80) != local_94)) {
            *(float *)(this + 0x78) = local_9c;
            *(float *)(this + 0x7c) = local_98;
            *(float *)(this + 0x80) = local_94;
          }
          local_40 = -*(float *)(this + 0xa8);
          local_48 = local_40 * *(float *)(this + 0x78);
          local_44 = local_40 * *(float *)(this + 0x7c);
          local_40 = local_40 * *(float *)(this + 0x80);
          FUN_006015e0(&local_48);
          local_84 = local_cc;
          local_80 = local_c8;
          local_7c = local_c4;
          in_stack_fffffebc = local_108;
          pfVar3 = (float *)operator+(in_stack_fffffebc,(vector_3d *)&local_38);
          local_78 = *pfVar3;
          local_74 = pfVar3[1];
          local_70 = pfVar3[2];
          uVar7 = operator-(local_f0,(vector_3d *)&local_78);
          FUN_006015e0(uVar7);
          local_3c = vector_3d::magnitude((vector_3d *)&local_2c);
          local_3c = local_3c / *(float *)(this + 0xb4);
          vector_3d::normalize((vector_3d *)&local_2c);
          vector_3d::operator*=((vector_3d *)&local_2c,(float *)(this + 0xa4));
          vector_3d::operator*=((vector_3d *)&local_2c,&local_3c);
          vector_3d::operator*=((vector_3d *)&local_2c,&frameLength);
          FUN_006af3f0(&local_2c);
          fVar10 = vector_3d::magnitude((vector_3d *)&local_2c);
          if (fVar10 < 0.5) {
            *(undefined4 *)(this + 0xe8) = 1;
          }
        }
        goto LAB_006af339;
      }
      if (*(int *)(this + 0x9c) == 0) {
        local_2c = *(float *)(this + 0x90) - local_1c;
        local_28 = *(float *)(this + 0x94) - local_18;
        local_24 = *(float *)(this + 0x98) - local_14;
        FUN_006015e0(&local_2c);
        local_2c = local_60;
        local_28 = local_5c;
        local_24 = local_58;
        local_20 = SQRT(local_5c * local_5c + local_58 * local_58 + local_60 * local_60);
        local_48 = local_38 - local_1c;
        local_44 = local_34 - local_18;
        local_40 = local_30 - local_14;
        FUN_006015e0(&local_48);
        local_8 = local_4c;
        local_10 = local_54;
        local_c = local_50;
        if (*(float *)(this + 0xa0) < local_20) {
          if (SQRT(local_50 * local_50 + local_4c * local_4c + local_54 * local_54) <= local_20) {
            local_1c = local_38;
            local_18 = local_34;
            local_b8 = local_30;
          }
          else {
            local_48 = local_2c + local_38;
            local_44 = local_28 + local_34;
            local_40 = local_24 + local_30;
            FUN_006015e0(&local_48);
            local_1c = local_c0;
            local_18 = local_bc;
          }
          *(undefined4 *)(this + 0x9c) = 1;
          local_14 = local_b8;
          goto LAB_006af339;
        }
        local_20 = (local_20 / *(float *)(this + 0xa0)) * *(float *)(this + 0xf4) +
                   *(float *)(this + 0xa4);
        fVar10 = vector_3d::magnitude((vector_3d *)&local_10);
        if (fVar10 != 0.0) {
          local_10 = local_10 / fVar10;
          local_c = local_c / fVar10;
          local_8 = local_8 / fVar10;
        }
        local_10 = local_10 * local_20 * frameLength;
        local_c = local_c * local_20 * frameLength;
        local_8 = local_8 * local_20 * frameLength;
        local_48 = local_38 - local_1c;
        local_44 = local_34 - local_18;
        local_40 = local_30 - local_14;
        FUN_006015e0(&local_48);
        fVar10 = local_10;
        if (SQRT(local_68 * local_68 + local_64 * local_64 + local_6c * local_6c) <
            SQRT(local_8 * local_8 + local_c * local_c + local_10 * local_10)) goto LAB_006af0df;
      }
      else {
        if (0.0 < *(float *)(this + 0xf8)) {
          *(undefined4 *)(this + 0xf0) = 0;
LAB_006af0df:
          local_1c = local_38;
          local_18 = local_34;
          local_14 = local_30;
          goto LAB_006af339;
        }
        local_20 = (0.0 / *(float *)(this + 0xa0)) * *(float *)(this + 0xf4) +
                   *(float *)(this + 0xa4);
        fVar10 = vector_3d::magnitude((vector_3d *)&local_10);
        if (fVar10 != 0.0) {
          local_10 = local_10 / fVar10;
          local_c = local_c / fVar10;
          local_8 = local_8 / fVar10;
        }
        local_c = local_c * local_20 * frameLength;
        local_8 = local_8 * local_20 * frameLength;
        fVar10 = local_10 * local_20 * frameLength;
      }
      local_1c = fVar10 + local_1c;
      local_18 = local_c + local_18;
      local_14 = local_8 + local_14;
      goto LAB_006af339;
    }
LAB_006af304:
    local_1c = local_38;
    local_14 = local_30;
    local_18 = local_34;
    if ((*(TerrainWindow **)(this + 0xb8) != (TerrainWindow *)0x0) &&
       ((iVar5 != 0 || (*(int *)(this + 0xb0) != 0)))) {
      TerrainWindow::update(*(TerrainWindow **)(this + 0xb8),1);
    }
  }
  else {
    if (*(int *)(this + 0xec) == 0) {
      if (iVar5 == 0) goto LAB_006aee3a;
      goto LAB_006af304;
    }
    local_2c = local_38 - local_1c;
    *(float *)(this + 0x90) = local_1c;
    *(undefined4 *)(this + 0x9c) = 0;
    local_28 = local_34 - local_18;
    *(float *)(this + 0x94) = local_18;
    *(float *)(this + 0x98) = local_14;
    local_24 = local_30 - local_14;
    FUN_006015e0(&local_2c);
    local_8 = local_ac;
    local_10 = local_b4;
    local_c = local_b0;
    fVar10 = vector_3d::magnitude((vector_3d *)&local_10);
    if (fVar10 != 0.0) {
      local_10 = local_10 / fVar10;
      local_c = local_c / fVar10;
      local_8 = local_8 / fVar10;
    }
    *(undefined4 *)(this + 0xf0) = 1;
    local_c = local_c * *(float *)(this + 0xa4) * frameLength;
    local_8 = local_8 * *(float *)(this + 0xa4) * frameLength;
    local_1c = local_10 * *(float *)(this + 0xa4) * frameLength + local_1c;
    local_18 = local_c + local_18;
    local_14 = local_8 + local_14;
  }
  *(undefined4 *)(this + 0xac) = 0;
LAB_006af339:
  FUN_006af3d0((vector_2d *)(this + 0x24));
  pvVar1 = (vector_2d *)(this + 0x2c);
  uVar7 = 0x6af351;
  pvVar11 = pvVar1;
  FUN_006af3d0(pvVar1);
  FUN_006015e0(&local_1c);
  setPosition(this,in_stack_fffffebc,uVar7,pvVar11);
  if ((*(TerrainWindow **)(this + 0xb8) != (TerrainWindow *)0x0) &&
     (((*(int *)(this + 0xac) != 0 || (*(int *)(this + 0xb0) != 0)) || (gamePaused != 0)))) {
    TerrainWindow::update(*(TerrainWindow **)(this + 0xb8),1);
  }
  if (land != (Terrain *)0x0) {
    Terrain::projectTerrain(land,(vector_3d *)(this + 0xbc),(vector_2d *)(this + 0x24),pvVar1);
  }
  *(undefined4 *)(this + 0xac) = 0;
  *(undefined4 *)(this + 0xb0) = 0;
                    /* END-> L:\mcx\Camera\Camera.cpp: ? */
  return 0;
}

