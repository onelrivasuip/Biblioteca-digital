from typing import Callable, Optional

import flet as ft

from models import Cliente, Libro


# Sombra suavecita que uso en todas las tarjetas para que no se vean tan planas.
CARD_SHADOW = ft.BoxShadow(
    spread_radius=0,
    blur_radius=10,
    color=ft.Colors.with_opacity(0.10, ft.Colors.SHADOW),
    offset=ft.Offset(0, 3),
)


# ---------------------------------------------------------------------------
# Piezas reutilizables (cada una es un @ft.control)
# ---------------------------------------------------------------------------


@ft.control
class LibroItem(ft.Container):
    """Una fila del inventario, un libro con su estado."""

    libro: Optional[Libro] = None
    nombre_cliente: Optional[str] = None

    def init(self):
        disponible = self.libro.disponible

        badge = ft.Container(
            content=ft.Text(
                self.libro.estado,
                size=12,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            bgcolor=ft.Colors.GREEN_600 if disponible else ft.Colors.ORANGE_700,
            padding=ft.Padding.symmetric(horizontal=12, vertical=5),
            border_radius=20,
        )

        subtitulo = f"ISBN: {self.libro.isbn}"
        if not disponible and self.nombre_cliente:
            subtitulo += f"   •   Prestado a: {self.nombre_cliente}"

        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(self.libro.titulo, weight=ft.FontWeight.BOLD, size=15),
                        ft.Text(f"por {self.libro.autor}", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text(subtitulo, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ],
                ),
                badge,
            ],
        )
        self.padding = 14
        self.bgcolor = ft.Colors.SURFACE_CONTAINER
        self.border = ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        self.border_radius = 10
        self.shadow = CARD_SHADOW


@ft.control
class ClienteItem(ft.Container):
    """Tarjetita de un cliente ya registrado, con sus iniciales de avatar."""

    cliente: Optional[Cliente] = None

    def init(self):
        iniciales = (self.cliente.nombre[:1] + self.cliente.apellido[:1]).upper()

        avatar = ft.CircleAvatar(
            content=ft.Text(iniciales, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLUE_700,
            radius=20,
        )

        self.content = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                avatar,
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(self.cliente.nombre_completo, weight=ft.FontWeight.BOLD, size=15),
                        ft.Text(f"Cédula: {self.cliente.cedula}", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ],
                ),
            ],
        )
        self.padding = 14
        self.bgcolor = ft.Colors.SURFACE_CONTAINER
        self.border = ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        self.border_radius = 10
        self.shadow = CARD_SHADOW


@ft.control
class PrestamoItem(ft.Container):
    """Fila de un préstamo activo, con botón para marcarlo como devuelto."""

    libro: Optional[Libro] = None
    nombre_cliente: Optional[str] = None
    on_devolver: Optional[Callable[[Libro], None]] = None

    def init(self):
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(self.libro.titulo, weight=ft.FontWeight.BOLD, size=15),
                        ft.Text(f"ISBN: {self.libro.isbn}", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text(
                            f"Prestado a: {self.nombre_cliente}",
                            size=13,
                            color=ft.Colors.ON_TERTIARY_CONTAINER,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                ),
                ft.Button(
                    "Devolver",
                    icon=ft.Icons.ASSIGNMENT_RETURN_OUTLINED,
                    bgcolor=ft.Colors.ORANGE_700,
                    color=ft.Colors.WHITE,
                    on_click=self.devolver_click,
                ),
            ],
        )
        self.padding = 14
        self.bgcolor = ft.Colors.TERTIARY_CONTAINER
        self.border = ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        self.border_radius = 10
        self.shadow = CARD_SHADOW

    def devolver_click(self, e):
        self.on_devolver(self.libro)


# ---------------------------------------------------------------------------
# Las tres vistas: libros, clientes y préstamos
# ---------------------------------------------------------------------------


@ft.control
class LibrosView(ft.Column):
    """Formulario para dar de alta libros + la lista del inventario."""

    libros: Optional[list] = None
    on_change: Optional[Callable[[], None]] = None

    def init(self):
        self.titulo_field = ft.TextField(label="Título", expand=True)
        self.autor_field = ft.TextField(label="Autor", expand=True)
        self.isbn_field = ft.TextField(label="ISBN", expand=True, on_submit=self.agregar_click)

        self.mensaje = ft.Text("", size=13)
        self.lista_libros = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=360)

        self.expand = True
        self.controls = [
            ft.Text("Registrar nuevo libro", size=18, weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(self.titulo_field, col={"sm": 12, "md": 4}),
                    ft.Container(self.autor_field, col={"sm": 12, "md": 4}),
                    ft.Container(self.isbn_field, col={"sm": 12, "md": 4}),
                ]
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        "Agregar libro",
                        icon=ft.Icons.ADD,
                        on_click=self.agregar_click,
                    ),
                    self.mensaje,
                ]
            ),
            ft.Divider(),
            ft.Text("Inventario", size=18, weight=ft.FontWeight.BOLD),
            self.lista_libros,
        ]
        self.refrescar_lista()

    def agregar_click(self, e):
        titulo = (self.titulo_field.value or "").strip()
        autor = (self.autor_field.value or "").strip()
        isbn = (self.isbn_field.value or "").strip()

        if not titulo or not autor or not isbn:
            self._mostrar_mensaje("⚠️  Título, autor e ISBN son obligatorios.", ft.Colors.RED)
            return

        if any(l.isbn.lower() == isbn.lower() for l in self.libros):
            self._mostrar_mensaje(f"⚠️  Ya existe un libro con el ISBN «{isbn}».", ft.Colors.RED)
            return

        self.libros.append(Libro(titulo, autor, isbn))

        self.titulo_field.value = ""
        self.autor_field.value = ""
        self.isbn_field.value = ""
        self._mostrar_mensaje(f"✅  «{titulo}» agregado al inventario.", ft.Colors.GREEN_700)

        self.refrescar_lista()
        self.update()
        self.on_change()

    def refrescar_lista(self, nombre_por_cedula: Optional[dict] = None):
        nombre_por_cedula = nombre_por_cedula or {}
        if not self.libros:
            self.lista_libros.controls = [
                ft.Text(
                    "No hay libros registrados todavía.",
                    italic=True,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            ]
        else:
            self.lista_libros.controls = [
                LibroItem(libro=libro, nombre_cliente=nombre_por_cedula.get(libro.cliente_cedula))
                for libro in reversed(self.libros)
            ]

    def _mostrar_mensaje(self, texto: str, color: str):
        self.mensaje.value = texto
        self.mensaje.color = color
        self.update()


@ft.control
class ClientesView(ft.Column):
    """Formulario para registrar clientes + el listado de todos."""

    clientes: Optional[list] = None
    on_change: Optional[Callable[[], None]] = None

    def init(self):
        self.nombre_field = ft.TextField(label="Nombre", expand=True)
        self.apellido_field = ft.TextField(label="Apellido", expand=True)
        self.cedula_field = ft.TextField(label="Cédula / ID", expand=True, on_submit=self.agregar_click)

        self.mensaje = ft.Text("", size=13)
        self.lista_clientes = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=360)

        self.expand = True
        self.controls = [
            ft.Text("Registrar nuevo cliente", size=18, weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(self.nombre_field, col={"sm": 12, "md": 4}),
                    ft.Container(self.apellido_field, col={"sm": 12, "md": 4}),
                    ft.Container(self.cedula_field, col={"sm": 12, "md": 4}),
                ]
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        "Agregar cliente",
                        icon=ft.Icons.PERSON_ADD_ALT_1,
                        on_click=self.agregar_click,
                    ),
                    self.mensaje,
                ]
            ),
            ft.Divider(),
            ft.Text("Clientes registrados", size=18, weight=ft.FontWeight.BOLD),
            self.lista_clientes,
        ]
        self.refrescar_lista()

    def agregar_click(self, e):
        nombre = (self.nombre_field.value or "").strip()
        apellido = (self.apellido_field.value or "").strip()
        cedula = (self.cedula_field.value or "").strip()

        if not nombre or not apellido or not cedula:
            self._mostrar_mensaje("⚠️  Nombre, apellido y cédula son obligatorios.", ft.Colors.RED)
            return

        if any(c.cedula.lower() == cedula.lower() for c in self.clientes):
            self._mostrar_mensaje(f"⚠️  Ya existe un cliente con la cédula «{cedula}».", ft.Colors.RED)
            return

        self.clientes.append(Cliente(nombre, apellido, cedula))

        self.nombre_field.value = ""
        self.apellido_field.value = ""
        self.cedula_field.value = ""
        self._mostrar_mensaje(f"✅  {nombre} {apellido} agregado.", ft.Colors.GREEN_700)

        self.refrescar_lista()
        self.update()
        self.on_change()

    def refrescar_lista(self):
        if not self.clientes:
            self.lista_clientes.controls = [
                ft.Text(
                    "No hay clientes registrados todavía.",
                    italic=True,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            ]
        else:
            self.lista_clientes.controls = [ClienteItem(cliente=c) for c in reversed(self.clientes)]

    def _mostrar_mensaje(self, texto: str, color: str):
        self.mensaje.value = texto
        self.mensaje.color = color
        self.update()


@ft.control
class PrestamosView(ft.Column):
    """Acá se prestan libros y se registran las devoluciones."""

    libros: Optional[list] = None
    clientes: Optional[list] = None
    on_change: Optional[Callable[[], None]] = None

    def init(self):
        self.dd_libro = ft.Dropdown(label="Libro disponible", expand=True)
        self.dd_cliente = ft.Dropdown(label="Cliente (buscar por nombre o cédula)", expand=True)
        self.mensaje = ft.Text("", size=13)
        self.lista_prestamos = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=300)

        self.expand = True
        self.controls = [
            ft.Text("Registrar préstamo", size=18, weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(self.dd_libro, col={"sm": 12, "md": 6}),
                    ft.Container(self.dd_cliente, col={"sm": 12, "md": 6}),
                ]
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        "Prestar libro",
                        icon=ft.Icons.SWAP_HORIZ,
                        on_click=self.prestar_click,
                    ),
                    self.mensaje,
                ]
            ),
            ft.Divider(),
            ft.Text("Préstamos activos", size=18, weight=ft.FontWeight.BOLD),
            self.lista_prestamos,
        ]
        self.refrescar()

    def refrescar(self):
        # Solo dejo prestar libros que están "Disponible".
        opciones_libro = [
            ft.dropdown.Option(key=l.isbn, text=f"{l.titulo} — {l.autor} (ISBN {l.isbn})")
            for l in self.libros
            if l.disponible
        ]
        self.dd_libro.options = opciones_libro
        if self.dd_libro.value not in {o.key for o in opciones_libro}:
            self.dd_libro.value = None

        opciones_cliente = [
            ft.dropdown.Option(key=c.cedula, text=f"{c.nombre_completo} — Cédula {c.cedula}")
            for c in self.clientes
        ]
        self.dd_cliente.options = opciones_cliente
        if self.dd_cliente.value not in {o.key for o in opciones_cliente}:
            self.dd_cliente.value = None

        nombre_por_cedula = {c.cedula: c.nombre_completo for c in self.clientes}
        prestados = [l for l in self.libros if not l.disponible]

        if not prestados:
            self.lista_prestamos.controls = [
                ft.Text(
                    "No hay préstamos activos en este momento.",
                    italic=True,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                )
            ]
        else:
            self.lista_prestamos.controls = [
                PrestamoItem(
                    libro=l,
                    nombre_cliente=nombre_por_cedula.get(l.cliente_cedula, "Cliente desconocido"),
                    on_devolver=self.devolver_libro,
                )
                for l in prestados
            ]

    def prestar_click(self, e):
        if not self.libros:
            self._mostrar_mensaje("⚠️  Primero registra al menos un libro.", ft.Colors.RED)
            return
        if not self.clientes:
            self._mostrar_mensaje("⚠️  Primero registra al menos un cliente.", ft.Colors.RED)
            return
        if not self.dd_libro.value:
            self._mostrar_mensaje("⚠️  Selecciona un libro disponible.", ft.Colors.RED)
            return
        if not self.dd_cliente.value:
            self._mostrar_mensaje("⚠️  Selecciona un cliente.", ft.Colors.RED)
            return

        libro = next((l for l in self.libros if l.isbn == self.dd_libro.value), None)

        # Por si el libro se prestó justo antes de darle clic al botón.
        if libro is None or not libro.disponible:
            self._mostrar_mensaje("⚠️  Ese libro ya no está disponible.", ft.Colors.RED)
            self.refrescar()
            self.update()
            return

        libro.prestar_a(self.dd_cliente.value)

        self.dd_libro.value = None
        self.dd_cliente.value = None
        self._mostrar_mensaje(f"✅  Préstamo registrado: «{libro.titulo}».", ft.Colors.GREEN_700)

        self.refrescar()
        self.update()
        self.on_change()

    def devolver_libro(self, libro: Libro):
        libro.devolver()
        self._mostrar_mensaje(f"↩️  Se registró la devolución de «{libro.titulo}».", ft.Colors.GREEN_700)
        self.refrescar()
        self.update()
        self.on_change()

    def _mostrar_mensaje(self, texto: str, color: str):
        self.mensaje.value = texto
        self.mensaje.color = color
        self.update()


# ---------------------------------------------------------------------------
# La app completa: junta las tres vistas y guarda los datos mientras corre
# ---------------------------------------------------------------------------


@ft.control
class BibliotecaApp(ft.Container):
    """El control raíz, arma todo lo de arriba en una sola pantalla."""

    def init(self):
        # Mientras la app esté abierta, todo vive acá (no se guarda en disco).
        self.libros: list = []
        self.clientes: list = []

        self.vista_libros = LibrosView(libros=self.libros, on_change=self.on_datos_cambiados)
        self.vista_clientes = ClientesView(clientes=self.clientes, on_change=self.on_datos_cambiados)
        self.vista_prestamos = PrestamosView(
            libros=self.libros, clientes=self.clientes, on_change=self.on_datos_cambiados
        )

        self.stat_total = self._crear_stat_card("Total de libros", "0", ft.Colors.BLUE_700, ft.Icons.MENU_BOOK)
        self.stat_disponibles = self._crear_stat_card(
            "Disponibles", "0", ft.Colors.GREEN_700, ft.Icons.CHECK_CIRCLE
        )
        self.stat_prestados = self._crear_stat_card("Prestados", "0", ft.Colors.ORANGE_700, ft.Icons.SWAP_HORIZ)
        self.stat_clientes = self._crear_stat_card("Clientes", "0", ft.Colors.PURPLE_700, ft.Icons.PEOPLE)

        self.stats_row = ft.ResponsiveRow(
            controls=[
                ft.Container(self.stat_total, col={"sm": 6, "md": 3}),
                ft.Container(self.stat_disponibles, col={"sm": 6, "md": 3}),
                ft.Container(self.stat_prestados, col={"sm": 6, "md": 3}),
                ft.Container(self.stat_clientes, col={"sm": 6, "md": 3}),
            ]
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            length=3,
            animation_duration=250,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Libros", icon=ft.Icons.MENU_BOOK),
                            ft.Tab(label="Clientes", icon=ft.Icons.PEOPLE),
                            ft.Tab(label="Préstamos", icon=ft.Icons.SWAP_HORIZ),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            ft.Container(content=self.vista_libros, padding=20),
                            ft.Container(content=self.vista_clientes, padding=20),
                            ft.Container(content=self.vista_prestamos, padding=20),
                        ],
                    ),
                ],
            ),
        )

        # Botón de sol/luna arriba a la derecha para cambiar de tema.
        self.theme_toggle = ft.IconButton(
            icon=ft.Icons.DARK_MODE_OUTLINED,
            tooltip="Cambiar a modo oscuro",
            icon_color=ft.Colors.ON_PRIMARY,
            on_click=self.toggle_theme,
        )

        encabezado = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.LOCAL_LIBRARY, color=ft.Colors.ON_PRIMARY, size=32),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text(
                                        "Biblioteca Central",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.ON_PRIMARY,
                                    ),
                                    ft.Text(
                                        "Sistema de control de libros, clientes y préstamos",
                                        size=12,
                                        color=ft.Colors.with_opacity(0.85, ft.Colors.ON_PRIMARY),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    self.theme_toggle,
                ],
            ),
            padding=20,
            bgcolor=ft.Colors.PRIMARY,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )

        self.content = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                encabezado,
                ft.Container(
                    content=ft.Column(
                        expand=True,
                        spacing=20,
                        controls=[self.stats_row, self.tabs],
                    ),
                    padding=20,
                ),
            ],
        )
        self.border = ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
        self.border_radius = 12
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_LOW
        self.shadow = CARD_SHADOW
        self.width = 1000

        self._actualizar_stats()

    def toggle_theme(self, e):
        page = self.page
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_toggle.icon = ft.Icons.DARK_MODE_OUTLINED
            self.theme_toggle.tooltip = "Cambiar a modo oscuro"
        else:
            page.theme_mode = ft.ThemeMode.DARK
            self.theme_toggle.icon = ft.Icons.LIGHT_MODE_OUTLINED
            self.theme_toggle.tooltip = "Cambiar a modo claro"
        page.update()

    @staticmethod
    def _crear_stat_card(titulo: str, valor: str, color: str, icono) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icono, color=color, size=20),
                            ft.Text(titulo, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                        ]
                    ),
                    ft.Text(valor, size=26, weight=ft.FontWeight.BOLD, color=color),
                ],
            ),
            padding=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            shadow=CARD_SHADOW,
        )

    def on_datos_cambiados(self):
        # Esto se dispara cada vez que algo cambia en libros o clientes.
        nombre_por_cedula = {c.cedula: c.nombre_completo for c in self.clientes}
        self.vista_libros.refrescar_lista(nombre_por_cedula)
        self.vista_clientes.refrescar_lista()
        self.vista_prestamos.refrescar()
        self._actualizar_stats()
        self.update()

    def _actualizar_stats(self):
        total = len(self.libros)
        disponibles = sum(1 for l in self.libros if l.disponible)
        prestados = total - disponibles

        self.stat_total.content.controls[1].value = str(total)
        self.stat_disponibles.content.controls[1].value = str(disponibles)
        self.stat_prestados.content.controls[1].value = str(prestados)
        self.stat_clientes.content.controls[1].value = str(len(self.clientes))


def main(page: ft.Page):
    page.title = "Sistema de Control de Biblioteca"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 30
    page.bgcolor = ft.Colors.SURFACE
    page.window.width = 1080
    page.window.height = 800
    page.window.min_width = 720

    page.add(ft.SafeArea(expand=True, content=BibliotecaApp()))


if __name__ == "__main__":
    ft.run(main)
