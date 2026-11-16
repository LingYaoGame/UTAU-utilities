#!/usr/bin/env python3
"""
OtoAligner — UTAU oto.ini batch fixer (PyQt5 · multilingual)
Supported languages: Chinese / English / Japanese / Korean
Dependency: pip install PyQt5

Timeline order constraint (offsets relative to offset):
    0 <= overlap <= preutterance <= consonant
    offset is absolute; consonant = 0 means no fixed point (common for CV).
"""

import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QGroupBox, QStatusBar, QComboBox,
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
    # ---------------------------- Chinese ----------------------------
    'zh': {
        'window_title':        'OtoAligner — UTAU oto.ini 批量修正工具',
        'lang_label':          '语言：',
        'input_group':         '① 输入（声库文件夹 或 oto.ini 文件）',
        'input_placeholder':   '选择声库文件夹，或直接指定 oto.ini 文件…',
        'choose_folder':       '选文件夹…',
        'choose_file':         '选文件…',
        'output_group':        '② 导出位置（保留相对目录结构）',
        'output_placeholder':  '选择导出文件夹…',
        'preview':             '🔍 预览修改',
        'run':                 '💾 执行并导出',
        'clear_log':           '🗑 清空日志',
        'log_group':           '日志',
        'ready':               '就绪',
        'status_previewing':   '预览中…',
        'status_processing':   '处理中…',

        'choose_input_title':  '选择声库文件夹',
        'choose_input_file_title': '选择 oto.ini',
        'choose_output_title': '选择导出文件夹',
        'filter_oto':          'oto.ini (oto.ini)',
        'filter_all':          '所有文件 (*)',

        'dialog_input_error':  '输入错误',
        'dialog_output_error': '输出错误',
        'dialog_missing_output_title': '缺少输出',
        'dialog_missing_output_msg':   '请先选择导出文件夹',
        'dialog_confirm_title':'确认',
        'dialog_same_dir':     '输出目录与输入目录相同，将覆盖原 oto.ini。\n建议先备份，是否继续？',
        'dialog_confirm_run':  '即将处理 {n} 个 oto.ini 文件，\n导出到：\n{out}\n\n是否继续？',
        'dialog_complete':     '完成',
        'dialog_complete_msg': '已导出 {saved} 个 oto.ini\n修正 {changed} 条\n\n{out}',
        'dialog_busy_title':   '任务进行中',
        'dialog_busy_msg':     '当前任务仍在运行，确定要退出吗？',

        'err_not_exists':      '输入路径不存在',
        'err_must_be_oto':     '输入文件必须是 oto.ini',
        'err_no_oto':          '该文件夹内未找到任何 oto.ini',
        'err_create_out':      '无法创建输出目录：{err}',

        'log_preview_header':  '===== 预览模式（不写入任何文件） =====',
        'log_input':           '输入: {path}',
        'log_found_files':     '共发现 {n} 个 oto.ini 文件',
        'log_preview_done':    '===== 预览结束：共 {total} 条，将修正 {changed} 条 =====',
        'log_status_preview_done': '预览完成：{total} 条中 {changed} 条需修正',
        'log_start':           '===== 开始执行 =====',
        'log_output':          '输出: {path}',
        'log_done':            '===== 完成 =====',
        'log_summary':         '总条目 {total}，修正 {changed}',
        'log_files_result':    '成功导出 {saved} 个文件，失败 {failed} 个',
        'log_status_done':     '完成：导出 {saved} 个文件，修正 {changed} 条',

        'log_read_fail':       '[读取失败] {name}: {err}',
        'log_unknown_enc':     '[编码未知] {name}，跳过',
        'log_file_header':     '● {rel}',
        'log_file_stat':       '   条目 {total}，需要修正 {changed}（原编码 {enc}）',
        'log_old':             '     原: {line}',
        'log_new':             '     新: {line}',
        'log_more':            '     ...（仅显示前 5 条）',
        'log_export_ok':       '✓ {rel} → {out}  (条目 {total}, 修正 {changed}, 原编码 {enc})',
        'log_export_fail':     '✗ 写入失败 {rel}: {err}',
    },

    # ---------------------------- English ----------------------------
    'en': {
        'window_title':        'OtoAligner — UTAU oto.ini Batch Fixer',
        'lang_label':          'Language:',
        'input_group':         '① Input (voicebank folder or oto.ini file)',
        'input_placeholder':   'Choose a voicebank folder or a specific oto.ini file…',
        'choose_folder':       'Folder…',
        'choose_file':         'File…',
        'output_group':        '② Export location (keeps relative directory structure)',
        'output_placeholder':  'Choose an export folder…',
        'preview':             '🔍 Preview',
        'run':                 '💾 Export',
        'clear_log':           '🗑 Clear Log',
        'log_group':           'Log',
        'ready':               'Ready',
        'status_previewing':   'Previewing…',
        'status_processing':   'Processing…',

        'choose_input_title':  'Select Voicebank Folder',
        'choose_input_file_title': 'Select oto.ini',
        'choose_output_title': 'Select Export Folder',
        'filter_oto':          'oto.ini (oto.ini)',
        'filter_all':          'All Files (*)',

        'dialog_input_error':  'Input Error',
        'dialog_output_error': 'Output Error',
        'dialog_missing_output_title': 'Missing Output',
        'dialog_missing_output_msg':   'Please choose an export folder first.',
        'dialog_confirm_title':'Confirm',
        'dialog_same_dir':     'The output folder is the same as the input folder.\nOriginal oto.ini will be overwritten.\nBackup first. Continue?',
        'dialog_confirm_run':  'About to process {n} oto.ini file(s).\nExport to:\n{out}\n\nContinue?',
        'dialog_complete':     'Done',
        'dialog_complete_msg': 'Exported {saved} oto.ini file(s)\nFixed {changed} entries\n\n{out}',
        'dialog_busy_title':   'Task Running',
        'dialog_busy_msg':     'A task is still running. Quit anyway?',

        'err_not_exists':      'Input path does not exist.',
        'err_must_be_oto':     'The input file must be oto.ini.',
        'err_no_oto':          'No oto.ini found in this folder.',
        'err_create_out':      'Cannot create output folder: {err}',

        'log_preview_header':  '===== Preview mode (no files will be written) =====',
        'log_input':           'Input: {path}',
        'log_found_files':     'Found {n} oto.ini file(s)',
        'log_preview_done':    '===== Preview done: {total} entries, {changed} to fix =====',
        'log_status_preview_done': 'Preview done: {changed} / {total} entries need fixing',
        'log_start':           '===== Start =====',
        'log_output':          'Output: {path}',
        'log_done':            '===== Done =====',
        'log_summary':         'Total {total}, fixed {changed}',
        'log_files_result':    '{saved} file(s) written, {failed} failed',
        'log_status_done':     'Done: {saved} file(s) written, {changed} entries fixed',

        'log_read_fail':       '[Read failed] {name}: {err}',
        'log_unknown_enc':     '[Unknown encoding] {name}, skipped',
        'log_file_header':     '● {rel}',
        'log_file_stat':       '   {total} entries, {changed} to fix (source encoding {enc})',
        'log_old':             '     old: {line}',
        'log_new':             '     new: {line}',
        'log_more':            '     ... (showing first 5 only)',
        'log_export_ok':       '✓ {rel} → {out}  ({total} entries, {changed} fixed, src {enc})',
        'log_export_fail':     '✗ Write failed {rel}: {err}',
    },

    # ---------------------------- Japanese ----------------------------
    'ja': {
        'window_title':        'OtoAligner — UTAU oto.ini 一括修正ツール',
        'lang_label':          '言語：',
        'input_group':         '① 入力（音源フォルダ または oto.ini ファイル）',
        'input_placeholder':   '音源フォルダを選択、または oto.ini を直接指定…',
        'choose_folder':       'フォルダ…',
        'choose_file':         'ファイル…',
        'output_group':        '② 出力先（相対ディレクトリ構造を保持）',
        'output_placeholder':  '出力フォルダを選択…',
        'preview':             '🔍 プレビュー',
        'run':                 '💾 実行して書き出す',
        'clear_log':           '🗑 ログをクリア',
        'log_group':           'ログ',
        'ready':               '準備完了',
        'status_previewing':   'プレビュー中…',
        'status_processing':   '処理中…',

        'choose_input_title':  '音源フォルダを選択',
        'choose_input_file_title': 'oto.ini を選択',
        'choose_output_title': '出力フォルダを選択',
        'filter_oto':          'oto.ini (oto.ini)',
        'filter_all':          'すべてのファイル (*)',

        'dialog_input_error':  '入力エラー',
        'dialog_output_error': '出力エラー',
        'dialog_missing_output_title': '出力先未指定',
        'dialog_missing_output_msg':   '先に出力フォルダを選択してください。',
        'dialog_confirm_title':'確認',
        'dialog_same_dir':     '出力先が入力フォルダと同じです。\n元の oto.ini を上書きします。\nバックアップを推奨。続行しますか？',
        'dialog_confirm_run':  '{n} 個の oto.ini を処理します。\n出力先：\n{out}\n\n続行しますか？',
        'dialog_complete':     '完了',
        'dialog_complete_msg': '{saved} 個の oto.ini を書き出しました\n{changed} 件を修正\n\n{out}',
        'dialog_busy_title':   'タスク実行中',
        'dialog_busy_msg':     'タスクが実行中です。終了しますか？',

        'err_not_exists':      '入力パスが存在しません。',
        'err_must_be_oto':     '入力ファイルは oto.ini である必要があります。',
        'err_no_oto':          'このフォルダに oto.ini が見つかりません。',
        'err_create_out':      '出力フォルダを作成できません：{err}',

        'log_preview_header':  '===== プレビュー（ファイルは書き込みません） =====',
        'log_input':           '入力: {path}',
        'log_found_files':     'oto.ini を {n} 個検出',
        'log_preview_done':    '===== プレビュー終了：全 {total} 件、修正対象 {changed} 件 =====',
        'log_status_preview_done': 'プレビュー完了：{total} 件中 {changed} 件を修正',
        'log_start':           '===== 実行開始 =====',
        'log_output':          '出力: {path}',
        'log_done':            '===== 完了 =====',
        'log_summary':         '合計 {total} 件、修正 {changed} 件',
        'log_files_result':    '{saved} 個書き出し成功、{failed} 個失敗',
        'log_status_done':     '完了：{saved} 個書き出し、{changed} 件修正',

        'log_read_fail':       '[読み込み失敗] {name}: {err}',
        'log_unknown_enc':     '[エンコーディング不明] {name}、スキップ',
        'log_file_header':     '● {rel}',
        'log_file_stat':       '   {total} 件、修正対象 {changed} 件（元エンコーディング {enc}）',
        'log_old':             '     旧: {line}',
        'log_new':             '     新: {line}',
        'log_more':            '     ...（最初の 5 件のみ表示）',
        'log_export_ok':       '✓ {rel} → {out}（{total} 件、{changed} 件修正、元 {enc}）',
        'log_export_fail':     '✗ 書き込み失敗 {rel}: {err}',
    },

    # ---------------------------- Korean ----------------------------
    'ko': {
        'window_title':        'OtoAligner — UTAU oto.ini 일괄 수정 도구',
        'lang_label':          '언어:',
        'input_group':         '① 입력 (음원 폴더 또는 oto.ini 파일)',
        'input_placeholder':   '음원 폴더를 선택하거나 oto.ini 파일을 직접 지정…',
        'choose_folder':       '폴더 선택…',
        'choose_file':         '파일 선택…',
        'output_group':        '② 내보내기 위치 (상대 디렉터리 구조 유지)',
        'output_placeholder':  '내보낼 폴더를 선택…',
        'preview':             '🔍 미리보기',
        'run':                 '💾 실행 및 내보내기',
        'clear_log':           '🗑 로그 지우기',
        'log_group':           '로그',
        'ready':               '준비 완료',
        'status_previewing':   '미리보기 중…',
        'status_processing':   '처리 중…',

        'choose_input_title':  '음원 폴더 선택',
        'choose_input_file_title': 'oto.ini 선택',
        'choose_output_title': '내보낼 폴더 선택',
        'filter_oto':          'oto.ini (oto.ini)',
        'filter_all':          '모든 파일 (*)',

        'dialog_input_error':  '입력 오류',
        'dialog_output_error': '출력 오류',
        'dialog_missing_output_title': '출력 미지정',
        'dialog_missing_output_msg':   '먼저 내보낼 폴더를 선택하세요.',
        'dialog_confirm_title':'확인',
        'dialog_same_dir':     '출력 폴더가 입력 폴더와 같습니다.\n원본 oto.ini가 덮어쓰여집니다.\n백업을 권장합니다. 계속할까요?',
        'dialog_confirm_run':  'oto.ini 파일 {n}개를 처리합니다.\n내보낼 위치:\n{out}\n\n계속할까요?',
        'dialog_complete':     '완료',
        'dialog_complete_msg': 'oto.ini {saved}개를 내보냈습니다\n{changed}개 항목 수정\n\n{out}',
        'dialog_busy_title':   '작업 진행 중',
        'dialog_busy_msg':     '작업이 아직 실행 중입니다. 종료할까요?',

        'err_not_exists':      '입력 경로가 존재하지 않습니다.',
        'err_must_be_oto':     '입력 파일은 oto.ini여야 합니다.',
        'err_no_oto':          '이 폴더에서 oto.ini를 찾을 수 없습니다.',
        'err_create_out':      '출력 폴더를 만들 수 없습니다: {err}',

        'log_preview_header':  '===== 미리보기 (파일을 쓰지 않습니다) =====',
        'log_input':           '입력: {path}',
        'log_found_files':     'oto.ini {n}개 발견',
        'log_preview_done':    '===== 미리보기 완료: 총 {total}개 중 {changed}개 수정 예정 =====',
        'log_status_preview_done': '미리보기 완료: {total}개 중 {changed}개 수정 필요',
        'log_start':           '===== 실행 시작 =====',
        'log_output':          '출력: {path}',
        'log_done':            '===== 완료 =====',
        'log_summary':         '총 {total}개, 수정 {changed}개',
        'log_files_result':    '{saved}개 파일 성공, {failed}개 실패',
        'log_status_done':     '완료: {saved}개 내보냄, {changed}개 수정',

        'log_read_fail':       '[읽기 실패] {name}: {err}',
        'log_unknown_enc':     '[인코딩 미확인] {name}, 건너뜀',
        'log_file_header':     '● {rel}',
        'log_file_stat':       '   {total}개 항목, {changed}개 수정 필요 (원본 인코딩 {enc})',
        'log_old':             '     이전: {line}',
        'log_new':             '     이후: {line}',
        'log_more':            '     ... (앞 5개만 표시)',
        'log_export_ok':       '✓ {rel} → {out}  ({total}개 항목, {changed}개 수정, 원본 {enc})',
        'log_export_fail':     '✗ 쓰기 실패 {rel}: {err}',
    },
}


def t(key, **kw):
    """Get text for the current language; fall back to Chinese if key is missing."""
    lang = CURRENT_LANG
    text = TR.get(lang, {}).get(key) or TR['zh'].get(key, key)
    if kw:
        try:
            return text.format(**kw)
        except (KeyError, IndexError):
            return text
    return text


# ============================================================
# Core correction logic
# ============================================================

DEFAULT_PREUTTERANCE = 200
DEFAULT_OVERLAP = 50
VCV_PREUTTERANCE = 300
VCV_OVERLAP = 100
VCV_CONSONANT = 450

OFFSET_MIN, OFFSET_MAX = -100, 5000
CONSONANT_MIN, CONSONANT_MAX = 0, 2000
CUTOFF_MIN, CUTOFF_MAX = -5000, 100
PREUTTERANCE_MIN, PREUTTERANCE_MAX = 0, 1000
OVERLAP_MIN, OVERLAP_MAX = 0, 500        # overlap must not be negative


def parse_oto_line(line):
    line = line.strip()
    if not line or line.startswith(('#', ';')):
        return None
    if '=' not in line:
        return None
    left, right = line.split('=', 1)
    filename = left.strip()
    if not filename:
        return None
    parts = [p.strip() for p in right.split(',')]
    if len(parts) < 6:
        return None
    try:
        alias = parts[0]
        vals = [float(parts[i]) for i in range(1, 6)]
    except (ValueError, IndexError):
        return None
    return filename, alias, {
        'offset': vals[0], 'consonant': vals[1], 'cutoff': vals[2],
        'preutterance': vals[3], 'overlap': vals[4],
    }


def is_vcv(alias):
    if ' ' in alias:
        return True
    kana_count = sum(1 for ch in alias if '\u3040' <= ch <= '\u30ff')
    return kana_count >= 2


def normalize_params(alias, params):
    """
    Normalize a set of parameters.
    Timeline order: 0 <= overlap <= preutterance <= consonant
    offset is absolute; overlap/preutterance/consonant are relative to offset.
    """
    p = params.copy()
    vcv = is_vcv(alias)

    # 1. Clamp boundaries
    p['offset']       = max(OFFSET_MIN,       min(OFFSET_MAX,       p['offset']))
    p['consonant']    = max(CONSONANT_MIN,    min(CONSONANT_MAX,    p['consonant']))
    p['cutoff']       = max(CUTOFF_MIN,       min(CUTOFF_MAX,       p['cutoff']))
    p['preutterance'] = max(PREUTTERANCE_MIN, min(PREUTTERANCE_MAX, p['preutterance']))
    p['overlap']      = max(0,                min(OVERLAP_MAX,      p['overlap']))

    # 2. CV / VCV defaults
    if vcv:
        if p['consonant'] == 0 or p['consonant'] < p['preutterance']:
            p['consonant'] = max(p['consonant'], VCV_CONSONANT)
        if p['preutterance'] == 0:
            p['preutterance'] = VCV_PREUTTERANCE
        if p['overlap'] == 0:
            p['overlap'] = VCV_OVERLAP
    else:
        if p['preutterance'] == 0 or p['preutterance'] > 400:
            p['preutterance'] = DEFAULT_PREUTTERANCE
        if p['overlap'] == 0:
            p['overlap'] = DEFAULT_OVERLAP

    # 3. Enforce timeline order
    if p['overlap'] < 0:
        p['overlap'] = 0
    if p['preutterance'] < p['overlap']:
        p['preutterance'] = p['overlap']
    if p['consonant'] > 0 and p['consonant'] < p['preutterance']:
        p['consonant'] = p['preutterance']

    # 4. Fix right boundary
    if p['cutoff'] >= 0:
        p['cutoff'] = -max(300.0, p['preutterance'] * 1.5)
    min_needed = max(p['preutterance'] - p['overlap'], 100)
    if abs(p['cutoff']) < min_needed:
        p['cutoff'] = -min_needed

    return p


def fmt_num(v):
    if abs(v) < 0.05:
        return "0"
    s = f"{v:.1f}"
    return s[:-2] if s.endswith('.0') else s


def format_oto_line(filename, alias, p):
    return (f"{filename}={alias},{fmt_num(p['offset'])},{fmt_num(p['consonant'])},"
            f"{fmt_num(p['cutoff'])},{fmt_num(p['preutterance'])},{fmt_num(p['overlap'])}")


def detect_encoding(raw):
    for enc in ('utf-8-sig', 'utf-8', 'shift_jis', 'cp932'):
        try:
            return enc, raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return None, None


def process_text(text):
    lines = text.splitlines()
    new_lines, samples = [], []
    total = changed = 0
    for line in lines:
        parsed = parse_oto_line(line)
        if parsed is None:
            new_lines.append(line)
            continue
        filename, alias, params = parsed
        total += 1
        new_params = normalize_params(alias, params)
        has_change = any(abs(new_params[k] - params[k]) > 0.01 for k in params)
        if has_change:
            changed += 1
            new_line = format_oto_line(filename, alias, new_params)
            new_lines.append(new_line)
            if len(samples) < 5:
                samples.append((line, new_line))
        else:
            new_lines.append(line)
    return '\n'.join(new_lines), total, changed, samples


# ============================================================
# Background workers
# ============================================================

class PreviewWorker(QThread):
    log = pyqtSignal(str, str)
    work_done = pyqtSignal(int, int)

    def __init__(self, items):
        super().__init__()
        self.items = items

    def run(self):
        total_all = changed_all = 0
        try:
            for base, f in self.items:
                if self.isInterruptionRequested():
                    break
                rel = f.relative_to(base)
                try:
                    enc, text = detect_encoding(f.read_bytes())
                except Exception as e:
                    self.log.emit(t('log_read_fail', name=rel, err=e), "error")
                    continue
                if text is None:
                    self.log.emit(t('log_unknown_enc', name=rel), "error")
                    continue

                _, total, changed, samples = process_text(text)
                total_all += total
                changed_all += changed

                self.log.emit(t('log_file_header', rel=rel), "header")
                self.log.emit(
                    t('log_file_stat', total=total, changed=changed, enc=enc), "info")
                for old, new in samples:
                    self.log.emit(t('log_old', line=old), "info")
                    self.log.emit(t('log_new', line=new), "info")
                if changed > 5:
                    self.log.emit(t('log_more'), "info")
                self.log.emit("", "info")
        finally:
            self.work_done.emit(total_all, changed_all)


class ExportWorker(QThread):
    log = pyqtSignal(str, str)
    work_done = pyqtSignal(int, int, int, int)

    def __init__(self, items, out_root):
        super().__init__()
        self.items = items
        self.out_root = out_root

    def run(self):
        total_all = changed_all = saved = failed = 0
        try:
            for base, f in self.items:
                if self.isInterruptionRequested():
                    break
                rel = f.relative_to(base)
                out_file = self.out_root / rel
                try:
                    enc, text = detect_encoding(f.read_bytes())
                except Exception as e:
                    self.log.emit(t('log_read_fail', name=rel, err=e), "error")
                    failed += 1
                    continue
                if text is None:
                    self.log.emit(t('log_unknown_enc', name=rel), "error")
                    failed += 1
                    continue

                new_text, total, changed, _ = process_text(text)
                total_all += total
                changed_all += changed

                try:
                    out_file.parent.mkdir(parents=True, exist_ok=True)
                    out_file.write_text(new_text, encoding='utf-8-sig')
                    saved += 1
                    self.log.emit(
                        t('log_export_ok', rel=rel, out=out_file,
                          total=total, changed=changed, enc=enc), "success")
                except Exception as e:
                    failed += 1
                    self.log.emit(
                        t('log_export_fail', rel=rel, err=e), "error")
        finally:
            self.work_done.emit(total_all, changed_all, saved, failed)


# ============================================================
# Main window
# ============================================================

class MainWindow(QMainWindow):
    COLORS = {
        'info':    '#24292f',
        'header':  '#0969da',
        'success': '#1a7f37',
        'error':   '#cf222e',
    }

    def __init__(self):
        super().__init__()
        self.resize(1000, 720)
        self._worker = None
        self._build_ui()
        self._apply_style()
        self._retranslate_ui()

    # ---------- UI (texts filled by _retranslate_ui) ----------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Top: language selection
        top = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        for code, name in LANG_NAMES:
            self.lang_combo.addItem(name, code)
        # Initial language
        for i, (code, _) in enumerate(LANG_NAMES):
            if code == CURRENT_LANG:
                self.lang_combo.setCurrentIndex(i)
                break
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        top.addWidget(self.lang_label)
        top.addWidget(self.lang_combo)
        top.addStretch(1)
        layout.addLayout(top)

        # Input
        self.input_group = QGroupBox()
        h1 = QHBoxLayout(self.input_group)
        h1.setContentsMargins(10, 12, 10, 10)
        self.input_edit = QLineEdit()
        self.btn_dir = QPushButton()
        self.btn_file = QPushButton()
        self.btn_dir.clicked.connect(self.choose_input_folder)
        self.btn_file.clicked.connect(self.choose_input_file)
        h1.addWidget(self.input_edit, 1)
        h1.addWidget(self.btn_dir)
        h1.addWidget(self.btn_file)
        layout.addWidget(self.input_group)

        # Output
        self.output_group = QGroupBox()
        h2 = QHBoxLayout(self.output_group)
        h2.setContentsMargins(10, 12, 10, 10)
        self.output_edit = QLineEdit()
        self.btn_out = QPushButton()
        self.btn_out.clicked.connect(self.choose_output)
        h2.addWidget(self.output_edit, 1)
        h2.addWidget(self.btn_out)
        layout.addWidget(self.output_group)

        # Action buttons
        h3 = QHBoxLayout()
        self.preview_btn = QPushButton()
        self.run_btn = QPushButton()
        self.clear_btn = QPushButton()
        self.preview_btn.clicked.connect(self.do_preview)
        self.run_btn.clicked.connect(self.do_run)
        self.clear_btn.clicked.connect(lambda: self.log_edit.clear())
        h3.addWidget(self.preview_btn)
        h3.addWidget(self.run_btn)
        h3.addWidget(self.clear_btn)
        h3.addStretch(1)
        layout.addLayout(h3)

        # Log
        self.log_group = QGroupBox()
        lv = QVBoxLayout(self.log_group)
        lv.setContentsMargins(10, 12, 10, 10)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Consolas", 9))
        self.log_edit.setStyleSheet(
            "background:#ffffff; color:#24292f; border:1px solid #d0d7de;")
        lv.addWidget(self.log_edit)
        layout.addWidget(self.log_group, 1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _retranslate_ui(self):
        """Refresh all static texts according to CURRENT_LANG."""
        self.setWindowTitle(t('window_title'))
        self.lang_label.setText(t('lang_label'))
        self.input_group.setTitle(t('input_group'))
        self.input_edit.setPlaceholderText(t('input_placeholder'))
        self.btn_dir.setText(t('choose_folder'))
        self.btn_file.setText(t('choose_file'))
        self.output_group.setTitle(t('output_group'))
        self.output_edit.setPlaceholderText(t('output_placeholder'))
        self.btn_out.setText(t('choose_folder'))
        self.preview_btn.setText(t('preview'))
        self.run_btn.setText(t('run'))
        self.clear_btn.setText(t('clear_log'))
        self.log_group.setTitle(t('log_group'))
        self.status.showMessage(t('ready'))

    def _on_lang_changed(self, idx):
        global CURRENT_LANG
        code = self.lang_combo.itemData(idx)
        if not code or code == CURRENT_LANG:
            return
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
            QPushButton:disabled { color: #9aa0a6; }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid #d0d7de;
                border-radius: 4px;
            }
        """)

    # ---------- Log ----------
    def append_log(self, text, level='info'):
        color = self.COLORS.get(level, '#24292f')
        cursor = self.log_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if level == 'header':
            fmt.setFontWeight(QFont.Bold)
        cursor.insertText(text + "\n", fmt)
        self.log_edit.setTextCursor(cursor)
        self.log_edit.ensureCursorVisible()

    # ---------- Path selection ----------
    def choose_input_folder(self):
        p = QFileDialog.getExistingDirectory(self, t('choose_input_title'))
        if p:
            self.input_edit.setText(p)

    def choose_input_file(self):
        p, _ = QFileDialog.getOpenFileName(
            self, t('choose_input_file_title'), "",
            f"{t('filter_oto')};;{t('filter_all')}")
        if p:
            self.input_edit.setText(p)

    def choose_output(self):
        p = QFileDialog.getExistingDirectory(self, t('choose_output_title'))
        if p:
            self.output_edit.setText(p)

    # ---------- File collection ----------
    def collect(self):
        src = Path(self.input_edit.text().strip())
        if not src.exists():
            raise ValueError(t('err_not_exists'))
        if src.is_file():
            if src.name.lower() != 'oto.ini':
                raise ValueError(t('err_must_be_oto'))
            return [(src.parent, src)]
        files = sorted(src.rglob('oto.ini'))
        if not files:
            raise ValueError(t('err_no_oto'))
        return [(src, f) for f in files]

    # ---------- Preview ----------
    def do_preview(self):
        if self._worker is not None and self._worker.isRunning():
            return
        try:
            items = self.collect()
        except Exception as e:
            QMessageBox.critical(self, t('dialog_input_error'), str(e))
            return

        self.log_edit.clear()
        self.append_log(t('log_preview_header'), 'header')
        self.append_log(t('log_input', path=self.input_edit.text()))
        self.append_log(t('log_found_files', n=len(items)))
        self.append_log("")

        self._set_busy(True, t('status_previewing'))

        w = PreviewWorker(items)
        w.log.connect(self.append_log)
        w.work_done.connect(self._on_preview_done)
        self._worker = w
        w.start()

    def _on_preview_done(self, total, changed):
        self.append_log(
            t('log_preview_done', total=total, changed=changed), 'header')
        self._set_busy(
            False, t('log_status_preview_done', total=total, changed=changed))
        self._worker = None

    # ---------- Export ----------
    def do_run(self):
        if self._worker is not None and self._worker.isRunning():
            return
        try:
            items = self.collect()
        except Exception as e:
            QMessageBox.critical(self, t('dialog_input_error'), str(e))
            return

        out_str = self.output_edit.text().strip()
        if not out_str:
            QMessageBox.warning(
                self, t('dialog_missing_output_title'),
                t('dialog_missing_output_msg'))
            return
        out_root = Path(out_str)
        try:
            out_root.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(
                self, t('dialog_output_error'),
                t('err_create_out', err=e))
            return

        src = Path(self.input_edit.text().strip())
        if src.is_dir() and out_root.resolve() == src.resolve():
            r = QMessageBox.question(
                self, t('dialog_confirm_title'), t('dialog_same_dir'),
                QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes:
                return

        r = QMessageBox.question(
            self, t('dialog_confirm_title'),
            t('dialog_confirm_run', n=len(items), out=out_root),
            QMessageBox.Yes | QMessageBox.No)
        if r != QMessageBox.Yes:
            return

        self.log_edit.clear()
        self.append_log(t('log_start'), 'header')
        self.append_log(t('log_input', path=src))
        self.append_log(t('log_output', path=out_root))
        self.append_log("")

        self._set_busy(True, t('status_processing'))

        w = ExportWorker(items, out_root)
        w.log.connect(self.append_log)
        w.work_done.connect(
            lambda tot, ch, sv, fl: self._on_export_done(tot, ch, sv, fl, out_root))
        self._worker = w
        w.start()

    def _on_export_done(self, total, changed, saved, failed, out_root):
        self.append_log("", 'info')
        self.append_log(t('log_done'), 'header')
        self.append_log(t('log_summary', total=total, changed=changed))
        self.append_log(
            t('log_files_result', saved=saved, failed=failed))
        self._set_busy(
            False, t('log_status_done', saved=saved, changed=changed))
        self._worker = None
        if failed == 0 and saved > 0:
            QMessageBox.information(
                self, t('dialog_complete'),
                t('dialog_complete_msg', saved=saved, changed=changed, out=out_root))

    # ---------- Helpers ----------
    def _set_busy(self, busy, msg=None):
        self.preview_btn.setEnabled(not busy)
        self.run_btn.setEnabled(not busy)
        if msg:
            self.status.showMessage(msg)

    def closeEvent(self, event):
        if self._worker is not None and self._worker.isRunning():
            r = QMessageBox.question(
                self, t('dialog_busy_title'), t('dialog_busy_msg'),
                QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes:
                event.ignore()
                return
            self._worker.requestInterruption()
            self._worker.wait(3000)
        event.accept()


# ============================================================
# Entry point
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
