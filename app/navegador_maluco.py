#!/usr/bin/env python3
"""Navegador Maluco — shell desktop GTK + WebKitGTK."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

import gi

gi.require_version("Gtk", "3.0")
try:
    gi.require_version("WebKit2", "4.1")
except ValueError:
    gi.require_version("WebKit2", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk, WebKit2

from core import HOME_URL, MAX_TABS, can_create_tab, is_youtube_shorts, normalize_input

APP_NAME = "Navegador Maluco"
APP_VERSION = "0.1.0"
APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "navegador-maluco"
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "navegador-maluco"
DOWNLOAD_DIR = Path.home() / "Downloads"

FOCUS_DEFAULTS = {
    "hide_homepage_feed": True, "hide_text_posts": True,
    "hide_and_redirect_subscriptions": True, "hide_explore_trending": True,
    "hide_more_from_youtube": True, "hide_irrelevant_search_results": True,
    "hide_shorts_tab": True, "hide_youtube_shorts": True, "disable_autoplay": True,
    "hide_end_screen_videowall": True, "hide_end_screen_cards": True,
    "disable_annotations": False, "hide_video_sidebar": False, "hide_recommended": True,
    "hide_live_chat": False, "hide_playlist": False, "hide_comments": False,
    "hide_profile_photos": False, "hide_mix_radio_playlists": False,
    "hide_merch_tickets_offers": True, "hide_video_info": False,
    "hide_video_buttons_bar": False, "hide_channel": False,
    "hide_video_description": False, "hide_top_header": False,
    "hide_notification_bell": False, "hide_homepage_shorts": True,
    "hide_search_shorts": True, "hide_channel_shorts": True, "hide_related_shorts": True,
    "hide_search_suggestions": False, "hide_miniplayer": False, "hide_feed_filters": False,
    "hide_promoted_content": True, "hide_membership_promotions": True,
    "block_shorts_navigation": True, "enable_personal_library": False,
    "enable_timestamp_bookmarks": False, "enable_video_notes": False,
    "enable_session_timer": False, "remember_channel_speed": False,
    "enable_study_mode": False,
}


class BrowserStore:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(DATA_DIR / "browser.sqlite3")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS favorites(
                url TEXT PRIMARY KEY, title TEXT NOT NULL, created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS history(
                id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL,
                title TEXT NOT NULL, visited_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS history_date ON history(visited_at DESC);
        """)
        self.db.commit()

    def add_history(self, url, title):
        if not url or not url.startswith(("http://", "https://")):
            return
        self.db.execute("INSERT INTO history(url,title,visited_at) VALUES(?,?,strftime('%s','now'))",
                        (url, title or url))
        self.db.execute("DELETE FROM history WHERE id NOT IN (SELECT id FROM history ORDER BY id DESC LIMIT 5000)")
        self.db.commit()

    def favorites(self):
        return self.db.execute("SELECT url,title FROM favorites ORDER BY created_at DESC LIMIT 1000").fetchall()

    def history(self):
        return self.db.execute("SELECT url,title FROM history ORDER BY visited_at DESC LIMIT 1000").fetchall()

    def is_favorite(self, url):
        return self.db.execute("SELECT 1 FROM favorites WHERE url=?", (url,)).fetchone() is not None

    def toggle_favorite(self, url, title):
        if self.is_favorite(url):
            self.db.execute("DELETE FROM favorites WHERE url=?", (url,))
        else:
            self.db.execute("INSERT OR REPLACE INTO favorites VALUES(?,?,strftime('%s','now'))",
                            (url, title or url))
        self.db.commit()

    def clear_history(self):
        self.db.execute("DELETE FROM history")
        self.db.commit()


class BrowserWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=APP_NAME)
        self.set_default_size(1120, 760)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.store = BrowserStore()
        self.config_path = CONFIG_DIR / "settings.json"
        self.settings = self.load_settings()
        self.webviews = {}
        self._download_context = WebKit2.WebContext.get_default()
        self._download_context.connect("download-started", self.on_download_started)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(root)
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        toolbar.set_border_width(7)
        root.pack_start(toolbar, False, False, 0)

        self.back_button = self.icon_button("go-previous", "Voltar", lambda *_: self.active_view().go_back() if self.active_view().can_go_back() else None)
        self.forward_button = self.icon_button("go-next", "Avançar", lambda *_: self.active_view().go_forward() if self.active_view().can_go_forward() else None)
        self.reload_button = self.icon_button("view-refresh", "Recarregar", lambda *_: self.active_view().reload())
        self.home_button = self.icon_button("go-home", "Página inicial", lambda *_: self.active_view().load_uri(HOME_URL))
        for button in (self.back_button, self.forward_button, self.reload_button, self.home_button):
            toolbar.pack_start(button, False, False, 0)

        self.address = Gtk.Entry()
        self.address.set_placeholder_text("Digite um endereço ou pesquise na web")
        self.address.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "system-search")
        self.address.connect("activate", self.on_address_activate)
        self.address.connect("icon-press", self.on_address_icon)
        toolbar.pack_start(self.address, True, True, 4)

        self.favorite_button = Gtk.Button(label="☆")
        self.favorite_button.set_tooltip_text("Adicionar/remover favorito")
        self.favorite_button.connect("clicked", self.on_toggle_favorite)
        toolbar.pack_start(self.favorite_button, False, False, 0)

        self.speed_button = Gtk.Button(label=f"{float(self.settings.get('playback_rate', 1.0)):g}×")
        self.speed_button.set_tooltip_text("Velocidade de reprodução")
        self.speed_button.connect("clicked", self.show_speed_menu)
        toolbar.pack_start(self.speed_button, False, False, 0)

        self.menu_button = Gtk.MenuButton()
        self.menu_button.set_image(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        self.menu_button.set_tooltip_text("Menu do navegador")
        self.menu_button.set_popup(self.build_menu())
        toolbar.pack_start(self.menu_button, False, False, 0)

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_group_name("navegador-maluco")
        self.notebook.connect("switch-page", self.on_switch_page)
        root.pack_start(self.notebook, True, True, 0)

        self.status = Gtk.Label(label="Pronto")
        self.status.set_xalign(0)
        self.status.set_margin_start(9)
        self.status.set_margin_end(9)
        self.status.set_margin_top(3)
        self.status.set_margin_bottom(4)
        root.pack_start(self.status, False, False, 0)

        self.connect("destroy", Gtk.main_quit)
        self.new_tab(HOME_URL)
        self.show_all()

    def load_settings(self):
        data = {"playback_rate": 1.0, "youtube_focus": dict(FOCUS_DEFAULTS)}
        try:
            saved = json.loads(self.config_path.read_text(encoding="utf-8"))
            data.update(saved)
            data["youtube_focus"] = {**FOCUS_DEFAULTS, **saved.get("youtube_focus", {})}
        except (OSError, ValueError, TypeError):
            pass
        return data

    def save_settings(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(self.settings, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def icon_button(icon, tooltip, callback):
        button = Gtk.Button()
        button.set_image(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON))
        button.set_tooltip_text(tooltip)
        button.connect("clicked", callback)
        return button

    def build_menu(self):
        menu = Gtk.Menu()
        items = [
            ("Nova aba", self.new_tab),
            ("Favoritos", self.show_favorites),
            ("Histórico", self.show_history),
            ("Downloads", self.show_downloads),
            ("YouTube sem distrações…", self.show_focus_settings),
            ("Limpar histórico", self.clear_history),
            ("Sobre o Navegador Maluco", self.show_about),
        ]
        for label, callback in items:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", lambda _item, cb=callback: cb())
            menu.append(item)
        menu.show_all()
        return menu

    def active_page(self):
        index = self.notebook.get_current_page()
        return self.notebook.get_nth_page(index) if index >= 0 else None

    def active_view(self):
        page = self.active_page()
        return getattr(page, "webview", None)

    def new_tab(self, url="about:blank"):
        if not can_create_tab(self.notebook.get_n_pages()):
            self.status.set_text(f"Limite de {MAX_TABS} abas atingido.")
            return None
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        view = WebKit2.WebView.new_with_context(self._download_context)
        page.webview = view
        page.url = url
        settings = view.get_settings()
        settings.set_enable_javascript(True)
        settings.set_enable_html5_database(True)
        settings.set_enable_html5_local_storage(True)
        settings.set_enable_developer_extras(False)
        view.connect("load-changed", self.on_load_changed, page)
        view.connect("load-failed", self.on_load_failed, page)
        view.connect("notify::title", self.on_title_changed, page)
        view.connect("decide-policy", self.on_decide_policy, page)
        view.connect("create", self.on_create_webview)
        view.connect("web-process-terminated", self.on_web_process_terminated, page)
        page.pack_start(view, True, True, 0)

        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        label = Gtk.Label(label="Nova aba")
        close = Gtk.Button.new_from_icon_name("window-close", Gtk.IconSize.MENU)
        close.set_relief(Gtk.ReliefStyle.NONE)
        close.set_focus_on_click(False)
        close.connect("clicked", self.close_tab_button, page)
        tab_box.pack_start(label, True, True, 0)
        tab_box.pack_start(close, False, False, 0)
        tab_box.show_all()
        page.tab_label = label
        page.tab_box = tab_box
        self.notebook.append_page(page, tab_box)
        self.notebook.set_tab_reorderable(page, True)
        self.notebook.set_current_page(self.notebook.page_num(page))
        self.webviews[page] = view
        page.show_all()
        if url and url != "about:blank":
            view.load_uri(url)
        else:
            self.address.set_text("")
            self.address.grab_focus()
        return view

    def close_tab_button(self, _button, page):
        index = self.notebook.page_num(page)
        if index >= 0:
            view = page.webview
            view.stop_loading()
            view.destroy()
            self.webviews.pop(page, None)
            self.notebook.remove_page(index)
        if self.notebook.get_n_pages() == 0:
            self.new_tab(HOME_URL)

    def on_create_webview(self, _view):
        view = self.new_tab("about:blank")
        return view

    def on_decide_policy(self, view, decision, decision_type):
        if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
            action = decision.get_navigation_action()
            request = action.get_request()
            uri = request.get_uri() or ""
            parsed = urlparse(uri)
            if parsed.scheme in {"http", "https", "about", "data", "blob"}:
                if self.settings["youtube_focus"].get("block_shorts_navigation", True) and is_youtube_shorts(uri):
                    decision.ignore()
                    view.load_uri("https://www.youtube.com/feed/subscriptions")
                    self.status.set_text("Navegação para YouTube Shorts bloqueada.")
                    return True
                decision.use()
                return True
            if parsed.scheme not in {"", "javascript"}:
                decision.ignore()
                try:
                    Gio.AppInfo.launch_default_for_uri(uri, None)
                except GLib.Error:
                    self.status.set_text("Não foi possível abrir esse endereço fora do navegador.")
                return True
        elif decision_type == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:
            action = decision.get_navigation_action()
            uri = action.get_request().get_uri()
            decision.ignore()
            if uri:
                new_view = self.new_tab(uri)
                return True
            return True
        return False

    def on_load_changed(self, view, event, page):
        if event == WebKit2.LoadEvent.STARTED:
            page.url = view.get_uri() or ""
            if page is self.active_page():
                self.address.set_text(page.url)
                self.status.set_text("Carregando…")
        elif event == WebKit2.LoadEvent.FINISHED:
            url = view.get_uri() or ""
            title = view.get_title() or url
            page.url = url
            self.store.add_history(url, title)
            if page is self.active_page():
                self.address.set_text(url)
                self.favorite_button.set_label("★" if self.store.is_favorite(url) else "☆")
                self.status.set_text(title[:160])
            self.inject_page_features(view, url)

    def inject_page_features(self, view, url):
        rate = float(self.settings.get("playback_rate", 1.0))
        media_script = """
        (() => {
          const rate = RATE;
          const apply = root => {
            if (root && root.querySelectorAll) root.querySelectorAll('video,audio').forEach(m => {
              try { m.playbackRate = rate; m.defaultPlaybackRate = rate; } catch (_) {}
            });
          };
          apply(document);
          document.addEventListener('play', e => {
            if (e.target instanceof HTMLMediaElement) {
              try { e.target.playbackRate = rate; } catch (_) {}
            }
          }, true);
          const observer = new MutationObserver(records => records.forEach(r =>
            r.addedNodes.forEach(n => { if (n.nodeType === 1) apply(n); })));
          observer.observe(document.documentElement, {childList:true, subtree:true});
        })();
        """.replace("RATE", str(rate))
        try:
            view.run_javascript(media_script, None, None, None)
            if urlparse(url).hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
                script_path = ASSET_DIR / "youtube-focus.js"
                if script_path.exists():
                    defaults = json.dumps(self.settings["youtube_focus"], ensure_ascii=False)
                    shim = """
                    (() => {
                      const defaults = DEFAULTS;
                      let store = {};
                      try { store = JSON.parse(localStorage.getItem('__nm_extension_storage') || '{}'); } catch (_) {}
                      store = Object.assign({}, defaults, store);
                      const persist = () => localStorage.setItem('__nm_extension_storage', JSON.stringify(store));
                      window.browser = window.browser || {};
                      window.browser.storage = {local: {
                        get: keys => Promise.resolve((() => {
                          if (keys === null || keys === undefined) return Object.assign({}, store);
                          if (typeof keys === 'string') return {[keys]: store[keys]};
                          if (Array.isArray(keys)) return Object.fromEntries(keys.map(k => [k, store[k]]));
                          const out = {}; Object.keys(keys).forEach(k => out[k] = store[k] === undefined ? keys[k] : store[k]); return out;
                        })()),
                        set: values => { Object.assign(store, values || {}); persist(); return Promise.resolve(); },
                        remove: keys => { (Array.isArray(keys) ? keys : [keys]).forEach(k => delete store[k]); persist(); return Promise.resolve(); },
                        clear: () => { store = {}; persist(); return Promise.resolve(); }
                      }};
                    })();
                    """.replace("DEFAULTS", defaults)
                    content = script_path.read_text(encoding="utf-8")
                    view.run_javascript(shim + "\n" + content, None, None, None)
        except (GLib.Error, TypeError) as exc:
            self.status.set_text(f"Não foi possível aplicar um recurso da página: {exc}")

    def on_load_failed(self, _view, _event, uri, error, page):
        self.status.set_text(f"Falha ao carregar {uri}: {error.message}")
        return False

    def on_title_changed(self, view, _param, page):
        title = view.get_title() or "Nova aba"
        page.tab_label.set_text(title[:34])

    def on_switch_page(self, _notebook, page, _number):
        if not page:
            return
        self.address.set_text(page.webview.get_uri() or "")
        url = page.webview.get_uri() or ""
        self.favorite_button.set_label("★" if self.store.is_favorite(url) else "☆")
        self.status.set_text(page.webview.get_title() or "Pronto")

    def on_address_activate(self, entry):
        try:
            uri = normalize_input(entry.get_text())
        except ValueError as exc:
            self.status.set_text(str(exc))
            return
        view = self.active_view()
        if view:
            view.load_uri(uri)
        else:
            self.new_tab(uri)

    def on_address_icon(self, _entry, _position, _event):
        self.address.grab_focus()

    def on_toggle_favorite(self, *_args):
        view = self.active_view()
        if not view:
            return
        url = view.get_uri() or ""
        if not url.startswith(("http://", "https://")):
            self.status.set_text("Somente páginas HTTP/HTTPS podem ser salvas.")
            return
        self.store.toggle_favorite(url, view.get_title() or url)
        self.favorite_button.set_label("★" if self.store.is_favorite(url) else "☆")

    def show_speed_menu(self, *_args):
        menu = Gtk.Menu()
        for rate in (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5):
            item = Gtk.MenuItem(label=f"{rate:g}×")
            item.connect("activate", self.set_playback_rate, rate)
            menu.append(item)
        menu.show_all()
        menu.popup_at_widget(self.speed_button, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None)

    def set_playback_rate(self, _item, rate):
        self.settings["playback_rate"] = rate
        self.speed_button.set_label(f"{rate:g}×")
        self.save_settings()
        view = self.active_view()
        if view:
            self.inject_page_features(view, view.get_uri() or "")

    def show_focus_settings(self, *_args):
        dialog = Gtk.Dialog(title="YouTube sem distrações", transient_for=self, flags=Gtk.DialogFlags.MODAL)
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)
        dialog.add_button("Salvar", Gtk.ResponseType.OK)
        dialog.set_default_size(520, 620)
        area = dialog.get_content_area()
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        box.set_border_width(12)
        widgets = {}
        labels = {
            "hide_homepage_feed":"Ocultar feed inicial", "hide_text_posts":"Ocultar publicações textuais",
            "hide_and_redirect_subscriptions":"Abrir YouTube nas inscrições", "hide_explore_trending":"Ocultar Explorar e Em alta",
            "hide_more_from_youtube":"Ocultar Mais do YouTube", "hide_irrelevant_search_results":"Ocultar blocos irrelevantes da pesquisa",
            "hide_shorts_tab":"Ocultar aba Shorts", "hide_youtube_shorts":"Ocultar vídeos Shorts",
            "block_shorts_navigation":"Bloquear navegação para Shorts", "disable_autoplay":"Desativar reprodução automática",
            "hide_recommended":"Ocultar recomendações", "hide_comments":"Ocultar comentários",
            "hide_live_chat":"Ocultar chat ao vivo", "hide_playlist":"Ocultar playlists laterais",
            "hide_video_sidebar":"Ocultar barra lateral do vídeo", "hide_promoted_content":"Ocultar espaços publicitários identificáveis",
            "hide_homepage_shorts":"Ocultar Shorts na página inicial", "hide_search_shorts":"Ocultar Shorts na pesquisa",
            "hide_channel_shorts":"Ocultar Shorts nos canais", "hide_related_shorts":"Ocultar Shorts relacionados",
            "hide_search_suggestions":"Ocultar sugestões da pesquisa", "hide_miniplayer":"Ocultar miniplayer",
            "enable_personal_library":"Ativar biblioteca pessoal de vídeos", "enable_timestamp_bookmarks":"Ativar marcação de momentos",
            "enable_video_notes":"Ativar anotações por vídeo", "enable_session_timer":"Ativar temporizador de sessão",
            "remember_channel_speed":"Lembrar velocidade por canal", "enable_study_mode":"Ativar modo estudo",
        }
        for key, label in labels.items():
            check = Gtk.CheckButton(label=label)
            check.set_active(bool(self.settings["youtube_focus"].get(key, FOCUS_DEFAULTS.get(key, False))))
            widgets[key] = check
            box.pack_start(check, False, False, 0)
        scroll.add(box)
        area.pack_start(scroll, True, True, 0)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            for key, widget in widgets.items():
                self.settings["youtube_focus"][key] = widget.get_active()
            self.save_settings()
            view = self.active_view()
            if view:
                view.reload()
        dialog.destroy()

    def show_list_dialog(self, title, rows):
        dialog = Gtk.Dialog(title=title, transient_for=self, flags=Gtk.DialogFlags.MODAL)
        dialog.add_button("Fechar", Gtk.ResponseType.CLOSE)
        dialog.set_default_size(760, 520)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_border_width(10)
        for url, label in rows:
            button = Gtk.Button(label=f"{(label or url)[:85]}\n{url[:115]}")
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.set_halign(Gtk.Align.FILL)
            button.connect("clicked", lambda _b, target=url: (self.active_view().load_uri(target), dialog.response(Gtk.ResponseType.CLOSE)))
            box.pack_start(button, False, False, 0)
        if not rows:
            box.pack_start(Gtk.Label(label="Nenhum item salvo."), False, False, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.add(box)
        dialog.get_content_area().pack_start(scroll, True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def show_favorites(self, *_args):
        self.show_list_dialog("Favoritos", self.store.favorites())

    def show_history(self, *_args):
        self.show_list_dialog("Histórico", self.store.history())

    def clear_history(self, *_args):
        dialog = Gtk.MessageDialog(transient_for=self, flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO,
            text="Limpar todo o histórico de navegação?")
        if dialog.run() == Gtk.ResponseType.YES:
            self.store.clear_history()
        dialog.destroy()

    def show_downloads(self, *_args):
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        try:
            Gio.AppInfo.launch_default_for_uri(DOWNLOAD_DIR.as_uri(), None)
        except GLib.Error:
            self.status.set_text(f"Downloads ficam em {DOWNLOAD_DIR}")

    def on_download_started(self, _context, download):
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        download.connect("decide-destination", self.on_download_destination)
        download.connect("failed", lambda _d, error: self.status.set_text(f"Download falhou: {error.message}"))
        download.connect("finished", lambda _d: self.status.set_text("Download concluído."))

    def on_download_destination(self, download, suggested_filename):
        safe_name = re.sub(r"[^A-Za-z0-9._ -]", "_", suggested_filename or "download")
        target = DOWNLOAD_DIR / safe_name
        counter = 1
        while target.exists():
            target = DOWNLOAD_DIR / f"{Path(safe_name).stem}-{counter}{Path(safe_name).suffix}"
            counter += 1
        download.set_destination(target.as_uri())
        self.status.set_text(f"Baixando para {target}")
        return True

    def on_web_process_terminated(self, _view, reason, _page):
        self.status.set_text(f"Processo da página encerrado ({reason}). Recarregue a aba.")

    def show_about(self, *_args):
        dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        dialog.set_program_name(APP_NAME)
        dialog.set_version(APP_VERSION)
        dialog.set_comments("Navegador desktop em desenvolvimento, com motor WebKitGTK.")
        dialog.set_website("https://github.com/MaluquinhoDev/NAvegadorMAlucoParaCOmputadorLinux")
        dialog.run()
        dialog.destroy()


def main():
    window = BrowserWindow()
    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
