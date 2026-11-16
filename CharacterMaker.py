#!/usr/bin/env python3
"""
CharacterMaker — UTAU character.txt generator (PyQt5 · multilingual)
Supported languages: Chinese / English / Japanese / Korean
Supported encodings: UTF-8 (BOM) / Shift-JIS / GBK
"""

import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QGroupBox, QStatusBar, QComboBox, QFormLayout, QSplitter
)

# ============================================================
# Multilingual (i18n)
# ============================================================

LANG_NAMES = [
    ('zh', '中文'),
    ('en', 'English'),
    ('ja', '日本語'),
    ('ko', '한국어'),
]

CURRENT_LANG = 'zh'

TR = {
    'zh': {
        'title': 'CharacterMaker — UTAU 声库信息生成工具',
        'lang': '语言：',
        'group_info': '① 基本信息',
        'group_creator': '② 创作者信息',
        'group_files': '③ 附加文件与链接',
        
        'name': '声库名称 (name) *',
        'version': '版本号 (version)',
        'image': '头像图片 (image)',
        'author': '作者 (author)',
        'voice': '声音提供者 (voice)',
        'sample': '试听音频 (sample)',
        'web': '网站链接 (web)',
        
        'name_ph': '例如：Hoshine Lala',
        'version_ph': '例如：1.0',
        'image_ph': '选择 icon.bmp (建议 100x100)',
        'author_ph': '例如：YourName',
        'voice_ph': '例如：CVName',
        'sample_ph': '选择 sample.wav',
        'web_ph': '例如：https://example.com',
        
        'btn_browse': '浏览…',
        'btn_save': '💾 生成 character.txt',
        'btn_clear': '🗑 清空',
        
        'encoding': '保存编码：',
        'enc_utf8': 'UTF-8 (带BOM，推荐)',
        'enc_sjis': 'Shift-JIS (日文)',
        'enc_gbk': 'GBK (中文)',
        
        'group_preview': '实时预览',
        'status_ready': '就绪',
        'status_saved': '已保存至: {path}',
        
        'dlg_err_title': '错误',
        'dlg_err_name': '“声库名称 (name)”是必填项！',
        'dlg_err_encoding': '保存失败：当前文本包含无法使用所选编码 ({enc}) 表示的字符。\n请更换编码或修改内容。\n\n详细错误：{err}',
        'dlg_save_title': '保存 character.txt',
        'dlg_save_success': 'character.txt 生成成功！\n\n编码：{enc}\n保存至：\n{path}',
        'filter_image': '图片文件 (*.bmp *.png *.jpg *.jpeg)',
        'filter_audio': '音频文件 (*.wav *.mp3 *.ogg)',
    },
    'en': {
        'title': 'CharacterMaker — UTAU Voicebank Info Generator',
        'lang': 'Language:',
        'group_info': '① Basic Info',
        'group_creator': '② Creator Info',
        'group_files': '③ Files & Links',
        
        'name': 'Voicebank Name (name) *',
        'version': 'Version (version)',
        'image': 'Image (image)',
        'author': 'Author (author)',
        'voice': 'Voice Provider (voice)',
        'sample': 'Sample (sample)',
        'web': 'Website (web)',
        
        'name_ph': 'e.g., Hoshine Lala',
        'version_ph': 'e.g., 1.0',
        'image_ph': 'Select icon.bmp (100x100 recommended)',
        'author_ph': 'e.g., YourName',
        'voice_ph': 'e.g., CVName',
        'sample_ph': 'Select sample.wav',
        'web_ph': 'e.g., https://example.com',
        
        'btn_browse': 'Browse…',
        'btn_save': '💾 Generate character.txt',
        'btn_clear': '🗑 Clear',
        
        'encoding': 'Encoding:',
        'enc_utf8': 'UTF-8 (BOM, Recommended)',
        'enc_sjis': 'Shift-JIS (Japanese)',
        'enc_gbk': 'GBK (Chinese)',
        
        'group_preview': 'Live Preview',
        'status_ready': 'Ready',
        'status_saved': 'Saved to: {path}',
        
        'dlg_err_title': 'Error',
        'dlg_err_name': 'Voicebank Name (name) is required!',
        'dlg_err_encoding': 'Save failed: The text contains characters that cannot be encoded in {enc}.\nPlease change the encoding or modify the text.\n\nDetails: {err}',
        'dlg_save_title': 'Save character.txt',
        'dlg_save_success': 'character.txt generated successfully!\n\nEncoding: {enc}\nSaved to:\n{path}',
        'filter_image': 'Image Files (*.bmp *.png *.jpg *.jpeg)',
        'filter_audio': 'Audio Files (*.wav *.mp3 *.ogg)',
    },
    'ja': {
        'title': 'CharacterMaker — UTAU 音源情報生成ツール',
        'lang': '言語：',
        'group_info': '① 基本情報',
        'group_creator': '② 制作者情報',
        'group_files': '③ ファイルとリンク',
        
        'name': '音源名 (name) *',
        'version': 'バージョン (version)',
        'image': 'アイコン画像 (image)',
        'author': '作者 (author)',
        'voice': '声の提供者 (voice)',
        'sample': 'サンプル音声 (sample)',
        'web': 'ウェブサイト (web)',
        
        'name_ph': '例：Hoshine Lala',
        'version_ph': '例：1.0',
        'image_ph': 'icon.bmp を選択 (100x100 推奨)',
        'author_ph': '例：YourName',
        'voice_ph': '例：CVName',
        'sample_ph': 'sample.wav を選択',
        'web_ph': '例：https://example.com',
        
        'btn_browse': '参照…',
        'btn_save': '💾 character.txt を生成',
        'btn_clear': '🗑 クリア',
        
        'encoding': '保存エンコード：',
        'enc_utf8': 'UTF-8 (BOM付き、推奨)',
        'enc_sjis': 'Shift-JIS (日本語)',
        'enc_gbk': 'GBK (中国語)',
        
        'group_preview': 'リアルタイムプレビュー',
        'status_ready': '準備完了',
        'status_saved': '保存先: {path}',
        
        'dlg_err_title': 'エラー',
        'dlg_err_name': '「音源名 (name)」は必須項目です！',
        'dlg_err_encoding': '保存失敗：選択したエンコード ({enc}) で表現できない文字が含まれています。\nエンコードを変更するか、テキストを修正してください。\n\n詳細: {err}',
        'dlg_save_title': 'character.txt を保存',
        'dlg_save_success': 'character.txt の生成に成功しました！\n\nエンコード: {enc}\n保存先：\n{path}',
        'filter_image': '画像ファイル (*.bmp *.png *.jpg *.jpeg)',
        'filter_audio': '音声ファイル (*.wav *.mp3 *.ogg)',
    },
    'ko': {
        'title': 'CharacterMaker — UTAU 음원 정보 생성 도구',
        'lang': '언어:',
        'group_info': '① 기본 정보',
        'group_creator': '② 제작자 정보',
        'group_files': '③ 파일 및 링크',
        
        'name': '음원 이름 (name) *',
        'version': '버전 (version)',
        'image': '아이콘 이미지 (image)',
        'author': '제작자 (author)',
        'voice': '음성 제공자 (voice)',
        'sample': '샘플 오디오 (sample)',
        'web': '웹사이트 (web)',
        
        'name_ph': '예: Hoshine Lala',
        'version_ph': '예: 1.0',
        'image_ph': 'icon.bmp 선택 (100x100 권장)',
        'author_ph': '예: YourName',
        'voice_ph': '예: CVName',
        'sample_ph': 'sample.wav 선택',
        'web_ph': '예: https://example.com',
        
        'btn_browse': '찾아보기…',
        'btn_save': '💾 character.txt 생성',
        'btn_clear': '🗑 초기화',
        
        'encoding': '저장 인코딩:',
        'enc_utf8': 'UTF-8 (BOM 포함, 권장)',
        'enc_sjis': 'Shift-JIS (일본어)',
        'enc_gbk': 'GBK (중국어)',
        
        'group_preview': '실시간 미리보기',
        'status_ready': '준비 완료',
        'status_saved': '저장 위치: {path}',
        
        'dlg_err_title': '오류',
        'dlg_err_name': '"음원 이름 (name)"은 필수 항목입니다!',
        'dlg_err_encoding': '저장 실패: 선택한 인코딩({enc})으로 표현할 수 없는 문자가 포함되어 있습니다.\n인코딩을 변경하거나 텍스트를 수정하세요.\n\n상세: {err}',
        'dlg_save_title': 'character.txt 저장',
        'dlg_save_success': 'character.txt가 성공적으로 생성되었습니다!\n\n인코딩: {enc}\n저장 위치:\n{path}',
        'filter_image': '이미지 파일 (*.bmp *.png *.jpg *.jpeg)',
        'filter_audio': '오디오 파일 (*.wav *.mp3 *.ogg)',
    }
}

def t(key, **kw):
    lang = CURRENT_LANG
    text = TR.get(lang, {}).get(key) or TR['zh'].get(key, key)
    if kw:
        try:
            return text.format(**kw)
        except KeyError:
            return text
    return text

# ============================================================
# Main window
# ============================================================

class CharacterMakerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(880, 650)
        self._build_ui()
        self._apply_style()
        self._retranslate_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        # Top: language selection
        top = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        for code, name in LANG_NAMES:
            self.lang_combo.addItem(name, code)
        for i, (code, _) in enumerate(LANG_NAMES):
            if code == CURRENT_LANG:
                self.lang_combo.setCurrentIndex(i)
                break
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        top.addWidget(self.lang_label)
        top.addWidget(self.lang_combo)
        top.addStretch(1)
        main_layout.addLayout(top)

        # Splitter: form on the left, preview on the right
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)

        # --- Left form area ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Basic information
        self.group_info = QGroupBox()
        form_info = QFormLayout(self.group_info)
        form_info.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.input_name = QLineEdit()
        self.input_version = QLineEdit()
        self.lbl_name = QLabel()
        self.lbl_version = QLabel()
        form_info.addRow(self.lbl_name, self.input_name)
        form_info.addRow(self.lbl_version, self.input_version)
        left_layout.addWidget(self.group_info)

        # 2. Creator information
        self.group_creator = QGroupBox()
        form_creator = QFormLayout(self.group_creator)
        form_creator.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.input_author = QLineEdit()
        self.input_voice = QLineEdit()
        self.lbl_author = QLabel()
        self.lbl_voice = QLabel()
        form_creator.addRow(self.lbl_author, self.input_author)
        form_creator.addRow(self.lbl_voice, self.input_voice)
        left_layout.addWidget(self.group_creator)

        # 3. Files and links
        self.group_files = QGroupBox()
        form_files = QFormLayout(self.group_files)
        form_files.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Image
        self.input_image = QLineEdit()
        self.btn_image = QPushButton()
        self.btn_image.clicked.connect(self._browse_image)
        h_img = QHBoxLayout()
        h_img.addWidget(self.input_image, 1)
        h_img.addWidget(self.btn_image)
        
        # Audio
        self.input_sample = QLineEdit()
        self.btn_sample = QPushButton()
        self.btn_sample.clicked.connect(self._browse_sample)
        h_samp = QHBoxLayout()
        h_samp.addWidget(self.input_sample, 1)
        h_samp.addWidget(self.btn_sample)
        
        # Link
        self.input_web = QLineEdit()
        
        self.lbl_image = QLabel()
        self.lbl_sample = QLabel()
        self.lbl_web = QLabel()
        
        form_files.addRow(self.lbl_image, h_img)
        form_files.addRow(self.lbl_sample, h_samp)
        form_files.addRow(self.lbl_web, self.input_web)
        left_layout.addWidget(self.group_files)
        
        left_layout.addStretch(1)

        # Bottom action buttons
        h_btns = QHBoxLayout()
        
        # Encoding combo box
        self.lbl_encoding = QLabel()
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItem("UTF-8 (BOM)", "utf-8-sig")
        self.encoding_combo.addItem("Shift-JIS", "cp932")
        self.encoding_combo.addItem("GBK", "gbk")
        
        self.btn_save = QPushButton()
        self.btn_save.setStyleSheet("background-color: #ffffff; color: #24292f; font-weight: bold; border: 1px solid #d0d7de;")
        self.btn_save.clicked.connect(self._save_file)
        self.btn_clear = QPushButton()
        self.btn_clear.clicked.connect(self._clear_inputs)
        
        h_btns.addWidget(self.lbl_encoding)
        h_btns.addWidget(self.encoding_combo)
        h_btns.addSpacing(15)
        h_btns.addWidget(self.btn_save)
        h_btns.addWidget(self.btn_clear)
        h_btns.addStretch(1)
        left_layout.addLayout(h_btns)

        splitter.addWidget(left_widget)

        # --- Right preview area ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.group_preview = QGroupBox()
        v_prev = QVBoxLayout(self.group_preview)
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setFont(QFont("Consolas", 11))
        self.text_preview.setStyleSheet("background-color: #f6f8fa; color: #1f2328; border: 1px solid #d0d7de;")
        v_prev.addWidget(self.text_preview)
        right_layout.addWidget(self.group_preview)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([480, 380])

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Bind live preview signals
        for line_edit in [self.input_name, self.input_version, self.input_image,
                          self.input_author, self.input_voice, self.input_sample, self.input_web]:
            line_edit.textChanged.connect(self._update_preview)

    def _retranslate_ui(self):
        self.setWindowTitle(t('title'))
        self.lang_label.setText(t('lang'))
        
        self.group_info.setTitle(t('group_info'))
        self.group_creator.setTitle(t('group_creator'))
        self.group_files.setTitle(t('group_files'))
        self.group_preview.setTitle(t('group_preview'))
        
        self.lbl_name.setText(t('name'))
        self.lbl_version.setText(t('version'))
        self.lbl_author.setText(t('author'))
        self.lbl_voice.setText(t('voice'))
        self.lbl_image.setText(t('image'))
        self.lbl_sample.setText(t('sample'))
        self.lbl_web.setText(t('web'))
        
        self.input_name.setPlaceholderText(t('name_ph'))
        self.input_version.setPlaceholderText(t('version_ph'))
        self.input_image.setPlaceholderText(t('image_ph'))
        self.input_author.setPlaceholderText(t('author_ph'))
        self.input_voice.setPlaceholderText(t('voice_ph'))
        self.input_sample.setPlaceholderText(t('sample_ph'))
        self.input_web.setPlaceholderText(t('web_ph'))
        
        self.btn_image.setText(t('btn_browse'))
        self.btn_sample.setText(t('btn_browse'))
        self.btn_save.setText(t('btn_save'))
        self.btn_clear.setText(t('btn_clear'))
        
        # Refresh encoding label and option texts
        self.lbl_encoding.setText(t('encoding'))
        self.encoding_combo.setItemText(0, t('enc_utf8'))
        self.encoding_combo.setItemText(1, t('enc_sjis'))
        self.encoding_combo.setItemText(2, t('enc_gbk'))
        
        self.status.showMessage(t('status_ready'))
        self._update_preview()

    def _on_lang_changed(self, idx):
        global CURRENT_LANG
        code = self.lang_combo.itemData(idx)
        if code and code != CURRENT_LANG:
            CURRENT_LANG = code
            self._retranslate_ui()

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget { font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif; font-size: 10pt; }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QPushButton {
                padding: 6px 16px;
                border: 1px solid #d0d7de;
                border-radius: 4px;
                background: #f6f8fa;
            }
            QPushButton:hover { background: #eef2f6; }
            QPushButton:pressed { background: #e1e6eb; }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #d0d7de;
                border-radius: 4px;
            }
        """)

    # ---------- Logic handlers ----------
    def _browse_image(self):
        p, _ = QFileDialog.getOpenFileName(
            self, t('image'), "", t('filter_image'))
        if p:
            self.input_image.setText(Path(p).name)

    def _browse_sample(self):
        p, _ = QFileDialog.getOpenFileName(
            self, t('sample'), "", t('filter_audio'))
        if p:
            self.input_sample.setText(Path(p).name)

    def _generate_text(self):
        """Generate character.txt content; empty values are omitted."""
        lines = []
        name = self.input_name.text().strip()
        if name:
            lines.append(f"name={name}")
        
        mapping = [
            ('version', self.input_version.text().strip()),
            ('image', self.input_image.text().strip()),
            ('author', self.input_author.text().strip()),
            ('voice', self.input_voice.text().strip()),
            ('sample', self.input_sample.text().strip()),
            ('web', self.input_web.text().strip())
        ]
        
        for key, val in mapping:
            if val:
                lines.append(f"{key}={val}")
                
        return "\n".join(lines)

    def _update_preview(self):
        text = self._generate_text()
        self.text_preview.setPlainText(text)

    def _clear_inputs(self):
        for line_edit in [self.input_name, self.input_version, self.input_image,
                          self.input_author, self.input_voice, self.input_sample, self.input_web]:
            line_edit.clear()

    def _save_file(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, t('dlg_err_title'), t('dlg_err_name'))
            return

        p, _ = QFileDialog.getSaveFileName(
            self, t('dlg_save_title'), "character.txt", "Text Files (*.txt);;All Files (*)")
        
        if not p:
            return
            
        if not p.lower().endswith('.txt'):
            p += '.txt'

        # Get selected encoding and its display name
        encoding_val = self.encoding_combo.currentData()
        encoding_name = self.encoding_combo.currentText()

        try:
            content = self._generate_text()
            Path(p).write_text(content, encoding=encoding_val)
            
            self.status.showMessage(t('status_saved', path=p))
            QMessageBox.information(
                self, t('dlg_save_title'), 
                t('dlg_save_success', enc=encoding_name, path=p)
            )
        except UnicodeEncodeError as e:
            # Handle characters unsupported by the encoding (e.g. Chinese in Shift-JIS)
            QMessageBox.critical(
                self, t('dlg_err_title'), 
                t('dlg_err_encoding', enc=encoding_name, err=e)
            )
        except Exception as e:
            QMessageBox.critical(self, t('dlg_err_title'), str(e))

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    win = CharacterMakerWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
