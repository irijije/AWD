# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['dimmer.py', 'window_manager.py', 'RNN.py'],
             pathex=['G:\\내 드라이브\\광주과학기술원\\수업\\IHCI\\AWD'],
             binaries=[],
             datas=[('ui\\', 'ui'), ('data.txt', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='dimmer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='ui\\icon.ico' )
