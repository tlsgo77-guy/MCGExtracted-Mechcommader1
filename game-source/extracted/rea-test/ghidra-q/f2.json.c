
/* systemInit */

void __cdecl systemInit(void)

{
  aSystem *paVar1;
  int iVar2;
  HWND__ *pHVar3;
  FitIniFile *pFVar4;
  intptr_t iVar5;
  intptr_t iVar6;
  uint uVar7;
  long lVar8;
  FastFile **ppFVar9;
  char *pcVar10;
  char *pcVar11;
  UINT UVar12;
  undefined1 local_124 [20];
  char local_110 [260];
  int local_c;
  int local_8;
  
                    /* START-> G:\mcx\HonorB.cpp: ? */
  uMessage = RegisterWindowMessageA(s_QueryCancelAutoPlay);
  iVar2 = FUN_00645360(s_system_cfg);
  if (iVar2 != 0) {
    ShowCursor(1);
    UVar12 = 0x30;
    pcVar11 = s_MechCommander_Closing_007a5d60;
    pcVar10 = s_MechCommander_Expansion_or_Edito;
    pHVar3 = aSystem::window(application);
    MessageBoxA(pHVar3,pcVar10,pcVar11,UVar12);
    killTheGame();
  }
  pFVar4 = File::operator_new(0x60);
  if (pFVar4 == (FitIniFile *)0x0) {
    pFVar4 = (FitIniFile *)0x0;
  }
  else {
    pFVar4 = (FitIniFile *)FitIniFile::FitIniFile(pFVar4);
  }
  iVar2 = (**(code **)(*(int *)pFVar4 + 4))(s_system_cfg,1,0x32);
  if (iVar2 == 0) {
    uVar7 = FUN_00649f70(s_systemHeap);
    if (uVar7 == 0) {
      uVar7 = FitIniFile::readIdULong(pFVar4,s_systemHeapSize,&systemHeapSize);
      if (uVar7 != 0) {
        Fatal(uVar7,s_Could_not_find_systemHeapSize___,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdULong(pFVar4,s_guiHeapSize,&guiHeapSize);
      if (uVar7 != 0) {
        Fatal(uVar7,s_Could_not_find_guiHeapSize___Usi,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdULong(pFVar4,s_logisticsHeapSize,&LogisticsHeapSize);
      if (uVar7 != 0) {
        pcVar10 = s_Could_not_find_logisticsHeapSize;
        goto LAB_00759202;
      }
    }
    else {
      pcVar10 = s_Could_not_find_systemHeap___Usin;
LAB_00759202:
      Fatal(uVar7,pcVar10,(char *)0x0);
    }
    iVar2 = FUN_00649f70(s_UseSound);
    useSound = (int)(iVar2 == 0);
    iVar2 = FUN_00649f70(s_UseMusic);
    if (iVar2 == 0) {
      useMusic = 1;
      if (useSound == 0) goto LAB_00759248;
    }
    else {
      useSound = 0;
LAB_00759248:
      useMusic = 0;
    }
    iVar2 = FUN_00649f70(s_DebugGameSystem);
    if (iVar2 == 0) {
      DebugGameSystem = 1;
    }
    iVar2 = FUN_00649f70(s_ABL);
    if (iVar2 != 0) {
      Fatal(0,s__Unable_to_find_ABL_settings__,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_SymbolTableHeapSize,&AblSymbolTableHeapSize);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_SymbolTableHe,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_StackHeapSize,&AblStackHeapSize);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_StackHeapSize,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_CodeHeapSize,&AblCodeHeapSize);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_CodeHeapSize_,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_RunTimeStackSize,&AblRunTimeStackSize);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_RunTimeStackS,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_MaxCodeBlockSize,&AblMaxCodeBlockSize);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_MaxCodeBlockS,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_MaxRegisteredModules,&AblMaxRegisteredModules);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_MaxRegistered,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_MaxStaticVariables,&AblMaxStaticVariables);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_MaxStaticVari,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_IncludeDebugInfo,&AblIncludeDebugInfo);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_IncludeDebugI,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdULong(pFVar4,s_DebuggerEnabled,&AblDebuggerEnabled);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_DebuggerEnabl,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdLong(pFVar4,s_MaxWatchesPerModule,&MaxWatchesPerModule);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_MaxWatchesPer,(char *)0x0);
    }
    uVar7 = FitIniFile::readIdLong(pFVar4,s_MaxBreakPointsPerModule,&MaxBreakPointsPerModule);
    if (uVar7 != 0) {
      Fatal(uVar7,s_Could_not_find_ABL_MaxBreakPoint,(char *)0x0);
    }
    uVar7 = FUN_00649f70(s_systemPaths);
    if (uVar7 == 0) {
      uVar7 = FitIniFile::readIdString(pFVar4,s_savePath,(char *)&savePath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_save_path_,(char *)0x0);
      }
      _sprintf(saveTempPath,s__stemp_,&savePath);
      __mkdir(saveTempPath);
      uVar7 = FitIniFile::readIdString(pFVar4,s_terrainPath_007a58dc,(char *)&terrainPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s_Could_not_find_terrain_path_007a58bc,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_palettePath,(char *)&palettePath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_palette_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_artPath,(char *)&artPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_art_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_fontPath,(char *)&fontPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_font_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_soundPath,(char *)&soundPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_sound_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_spritePath,(char *)&spritePath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s_Could_not_find_sprite_path_007a57f0,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_shapesPath,shapesPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_shapes_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_objectPath,objectPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_object_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_missionPath,missionPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_mission_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_warriorPath,(char *)&warriorPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_warrior_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_profilePath,(char *)&profilePath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_profile_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_cameraPath,cameraPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_camera_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_tilePath,tilePath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_tile_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_tile90Path,tile90Path,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_tile90_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_interfacePath,(char *)&interfacePath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_interface_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_moviePath,moviePath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_movie_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_missionName,(char *)&missionName,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_Mission_File_Nam,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_CDsoundPath,(char *)&CDsoundPath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_CD_sound_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_CDspritePath,(char *)&CDspritePath,0x4f);
      if (uVar7 != 0) {
        Fatal(uVar7,s__Could_not_find_CD_sprite_path_,(char *)0x0);
      }
      uVar7 = FitIniFile::readIdString(pFVar4,s_CDmoviePath,CDmoviePath,0x4f);
      if (uVar7 != 0) {
        pcVar10 = s__Could_not_find_CD_movie_path_;
        goto LAB_0075976f;
      }
    }
    else {
      pcVar10 = s_Could_not_find_systemPaths___Usi;
LAB_0075976f:
      Fatal(uVar7,pcVar10,(char *)0x0);
    }
    iVar5 = __findfirst(s___fst,local_124);
    iVar6 = iVar5;
    while (iVar6 != -1) {
      maxFastFiles = maxFastFiles + 1;
      iVar6 = __findnext(iVar5,local_124);
    }
    __findclose(iVar5);
    if (maxFastFiles != 0) {
      fastFiles = _malloc(maxFastFiles << 2);
      ppFVar9 = fastFiles;
      for (lVar8 = maxFastFiles; lVar8 != 0; lVar8 = lVar8 + -1) {
        *ppFVar9 = (FastFile *)0x0;
        ppFVar9 = ppFVar9 + 1;
      }
      iVar5 = __findfirst(s___fst,local_124);
      iVar6 = iVar5;
      while (iVar6 != -1) {
        FastFileInit(local_110);
        iVar6 = __findnext(iVar5,local_124);
      }
      __findclose(iVar5);
    }
    (**(code **)(*(int *)pFVar4 + 0xc))();
  }
  else {
    ShowCursor(1);
    UVar12 = 0x30;
    pcVar11 = s_MechCommander_Closing_007a5d60;
    pcVar10 = s_MechCommander_Expansion_or_Edito;
    pHVar3 = aSystem::window(application);
    MessageBoxA(pHVar3,pcVar10,pcVar11,UVar12);
    killTheGame();
  }
  if (pFVar4 != (FitIniFile *)0x0) {
    FitIniFile::~FitIniFile(pFVar4);
    File::operator_delete(pFVar4);
  }
  pFVar4 = File::operator_new(0x60);
  if (pFVar4 == (FitIniFile *)0x0) {
    pFVar4 = (FitIniFile *)0x0;
  }
  else {
    pFVar4 = (FitIniFile *)FitIniFile::FitIniFile(pFVar4);
  }
  uVar7 = (**(code **)(*(int *)pFVar4 + 4))(s_prefs_cfg,1,0x32);
  if (uVar7 != 0) {
    Fatal(uVar7,s_Could_not_open_prefs_cfg_,(char *)0x0);
    goto LAB_00759b00;
  }
  uVar7 = FUN_00649f70(s_MechCommander);
  if (uVar7 != 0) {
    Fatal(uVar7,s_Could_not_find_MechCommander_Pre,(char *)0x0);
    goto LAB_00759b00;
  }
  lVar8 = FitIniFile::readIdBoolean(pFVar4,s_PaletteCycle,(int *)(application + 0x4c8));
  paVar1 = application;
  if (lVar8 != 0) {
    *(undefined4 *)(application + 0x4c8) = 0;
  }
  lVar8 = FitIniFile::readIdLong(pFVar4,s_Gamma,(long *)(paVar1 + 2000));
  if (lVar8 != 0) {
    *(undefined4 *)(application + 2000) = 0;
  }
  lVar8 = FitIniFile::readIdBoolean(pFVar4,s_Use90Pixel,&use90PixelSprite);
  if (lVar8 != 0) {
    use90PixelSprite = 0;
  }
  lVar8 = FitIniFile::readIdBoolean(pFVar4,s_Force45Pixel,&only45Pixel);
  if (lVar8 != 0) {
    only45Pixel = 0;
  }
  if (use90PixelSprite == 0) {
LAB_00759947:
    if (only45Pixel == 0) {
      only45Pixel = 1;
    }
  }
  else if (only45Pixel != 0) {
    use90PixelSprite = 0;
    goto LAB_00759947;
  }
  lVar8 = FitIniFile::readIdBoolean(pFVar4,s_Force32Mb,&force32MB);
  if (lVar8 != 0) {
    force32MB = 0;
  }
  lVar8 = FitIniFile::readIdBoolean(pFVar4,s_Force16Mb,&force16MB);
  if (lVar8 == 0) {
    if ((force16MB != 0) && (force32MB != 0)) {
      force32MB = 0;
    }
  }
  else {
    force16MB = 0;
  }
  local_8 = 0;
  lVar8 = FitIniFile::readIdBoolean(pFVar4,s_DirectDraw,&local_8);
  if (lVar8 == 0) {
    gFullScreen = 1;
    if (local_8 == 0) goto LAB_007599c8;
  }
  else {
    local_8 = 0;
LAB_007599c8:
    gFullScreen = 0;
  }
  lVar8 = FitIniFile::readIdLong(pFVar4,s_Resolution,&local_c);
  if (lVar8 == 0) {
    if (local_c == 1) {
      displayMode = 1;
      displayWidth = 800;
      displayHeight = 600;
    }
    else if (local_c == 2) {
      displayMode = 2;
      displayWidth = 0x400;
      displayHeight = 0x300;
    }
    else if (local_c == 3) {
      displayMode = 3;
      displayWidth = 0x500;
      displayHeight = 0x400;
    }
  }
  lVar8 = FitIniFile::readIdLong(pFVar4,s_Language_0079efa8,&languageOffset);
  if (lVar8 != 0) {
    languageOffset = 0;
  }
  lVar8 = FitIniFile::readIdLong(pFVar4,s_Difficulty,&GameDifficulty);
  if (lVar8 != 0) {
    GameDifficulty = 1;
  }
  lVar8 = FitIniFile::readIdLong(pFVar4,s_Brightness,(long *)(application + 2000));
  if (lVar8 != 0) {
    *(undefined4 *)(application + 2000) = 0;
  }
  lVar8 = FitIniFile::readIdLong(pFVar4,s_MusicVolume_0079f018,&MusicVolume);
  if (lVar8 != 0) {
    MusicVolume = 0x40;
  }
  lVar8 = FitIniFile::readIdLong(pFVar4,s_RadioVolume,&RadioVolume);
  if (lVar8 != 0) {
    RadioVolume = 0x40;
  }
  lVar8 = FitIniFile::readIdLong(pFVar4,s_SFXVolume,&SFXVolume);
  if (lVar8 != 0) {
    SFXVolume = 0x60;
  }
LAB_00759b00:
  (**(code **)(*(int *)pFVar4 + 0xc))();
  if (pFVar4 != (FitIniFile *)0x0) {
    FitIniFile::~FitIniFile(pFVar4);
    File::operator_delete(pFVar4);
  }
  checkForCDInDrive(1,false);
  return;
}

