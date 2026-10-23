
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* public void __thiscall Terrain::projectTerrain(class vector_3d &,
                                                  class vector_2d &,
                                                  class vector_2d &) 
   public: void __thiscall Terrain::projectTerrain(class vector_3d &,class vector_2d &,class
   vector_2d &) */

void __thiscall
Terrain::projectTerrain(Terrain *this,vector_3d *param_1,vector_2d *param_2,vector_2d *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  short sVar5;
  short sVar6;
  
                    /* START-> L:\mcx\Terrain\Terrain.cpp: ? */
  fVar1 = _DAT_008099ac - *(float *)(param_1 + 4);
  fVar2 = *(float *)param_1 - _mapTopLeft3d100;
  fVar3 = (fVar2 - fVar1) * *(float *)(this + 0x28);
  *(float *)param_2 = fVar3;
  _floor((double)fVar3);
  sVar5 = __ftol();
  *(float *)param_2 = (float)(int)sVar5 + _mapTopLeft2d100;
  fVar1 = (fVar2 + fVar1) * *(float *)(this + 0x24);
  *(float *)(param_2 + 4) = fVar1;
  _floor((double)fVar1);
  sVar5 = __ftol();
  *(float *)(param_2 + 4) = (float)(int)sVar5;
  _floor((double)*(float *)(param_1 + 8));
  sVar6 = __ftol();
  fVar1 = *(float *)(param_1 + 4);
  fVar2 = *(float *)(param_1 + 8);
  *(float *)(param_2 + 4) = (_DAT_0080948c - (float)(int)sVar6) + (float)(int)sVar5;
  fVar4 = _DAT_008099c4 - fVar1 * 0.5;
  fVar1 = *(float *)param_1 * 0.5 - _mapTopLeft3d50;
  fVar3 = (fVar1 - fVar4) * *(float *)(this + 0x28);
  *(float *)param_3 = fVar3;
  _floor((double)fVar3);
  sVar5 = __ftol();
  *(float *)param_3 = (float)(int)sVar5 + _mapTopLeft2d50;
  fVar1 = (fVar1 + fVar4) * *(float *)(this + 0x24);
  *(float *)(param_3 + 4) = fVar1;
  _floor((double)fVar1);
  sVar5 = __ftol();
  *(float *)(param_3 + 4) = (float)(int)sVar5;
  _floor((double)(fVar2 * 0.5));
  sVar6 = __ftol();
  *(float *)(param_3 + 4) = (_DAT_008099bc - (float)(int)sVar6) + (float)(int)sVar5;
  return;
}

