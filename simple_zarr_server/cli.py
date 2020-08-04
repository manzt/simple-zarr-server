import click
from simple_zarr_server.server import serve
import zarr
from uvicorn.config import (
    HTTP_PROTOCOLS,
    LIFESPAN,
    LOOP_SETUPS,
    WS_PROTOCOLS,
)

HTTP_CHOICES = click.Choice(HTTP_PROTOCOLS.keys())
WS_CHOICES = click.Choice(WS_PROTOCOLS.keys())
LIFESPAN_CHOICES = click.Choice(LIFESPAN.keys())
LOOP_CHOICES = click.Choice([key for key in LOOP_SETUPS.keys() if key != "none"])


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--cors",
    type=str,
    default=None,
    help="Origin to allow CORS. Use wildcard '*' to allow all.",
)
@click.option(
    "--allow-write",
    "-w",
    help="Whether to allow PUT requests and enable write to underlying store.",
    is_flag=True,
)
# These options are mostly copied from uvicorn's docs
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Bind socket to this host.",
    show_default=True,
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Bind socket to this port.",
    show_default=True,
)
@click.option(
    "--debug", is_flag=True, default=False, help="Enable debug mode.", hidden=True
)
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload.")
@click.option(
    "--loop",
    type=LOOP_CHOICES,
    default="auto",
    help="Event loop implementation.",
    show_default=True,
)
@click.option(
    "--http",
    type=HTTP_CHOICES,
    default="auto",
    help="HTTP protocol implementation.",
    show_default=True,
)
@click.option(
    "--ws",
    type=WS_CHOICES,
    default="auto",
    help="WebSocket protocol implementation.",
    show_default=True,
)
@click.option(
    "--use-colors/--no-use-colors",
    is_flag=True,
    default=None,
    help="Enable/Disable colorized logging.",
)
@click.option(
    "--proxy-headers/--no-proxy-headers",
    is_flag=True,
    default=True,
    help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info.",
)
@click.option(
    "--forwarded-allow-ips",
    type=str,
    default=None,
    help="Comma seperated list of IPs to trust with proxy headers. Defaults to the $FORWARDED_ALLOW_IPS environment variable if available, or '127.0.0.1'.",
)
def main(
    path,
    cors,
    allow_write,
    host,
    port,
    loop,
    http,
    ws,
    debug,
    reload,
    proxy_headers,
    forwarded_allow_ips,
    use_colors,
):
    # Handles opening .n5, .zip, and .zarr extensions
    z = zarr.open(path, mode="a" if allow_write else "r")
    config = {
        "host": host,
        "port": port,
        "loop": loop,
        "http": http,
        "ws": ws,
        "debug": debug,
        "reload": reload,
        "proxy_headers": proxy_headers,
        "forwarded_allow_ips": forwarded_allow_ips,
        "use_colors": use_colors,
    }
    serve(z, allowed_origins=[cors], **config)
