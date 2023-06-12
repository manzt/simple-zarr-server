from __future__ import annotations

import numpy as np
import uvicorn
import zarr
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.routing import Mount, Route


def create_zarr_route(z: zarr.Array | zarr.Group) -> Route:
    """Creates a Starlette app, mapping HTTP requests on top of a Zarr store.

    Parameters
    ----------
    z : zarr.Array or zarr.Group
        Part of zarr hierarchy to expose over HTTP. The `read_only` property is
        checked to determine which HTTP methods are available.

    Returns
    -------
    route : starlette.routing.Route
        Route object that can be added to a Starlette app.
    """
    # Use read_only property to determine how the underlying store should be protected.
    methods = ["GET", "HEAD", "PUT"] if not z.read_only else ["GET", "HEAD"]
    # If z isn't the root of a hierarchy, need to prepend it's path.
    path_prefix = f"{z.path}/" if z.path else ""

    async def map_request(request):
        path = path_prefix + request.path_params["path"]
        if request.method == "PUT":
            # PUT only handled if writeable
            try:
                blob = await request.body()
                z.store[path] = blob
                return Response(status_code=200)
            except Exception:
                return Response(status_code=404)
        else:
            try:
                # Return blob if GET, otherwise it's HEAD and should return empty body
                body = z.store[path]
                if request.method == "HEAD":
                    body = None
                return Response(body, status_code=200)
            except KeyError:
                # Key not in store, return 404
                return Response(status_code=404)

    return Route("/{path:path}", endpoint=map_request, methods=methods)


def serve(
    source: zarr.Array | zarr.Group | np.ndarray,
    *,
    name: str | None = None,
    allowed_origins: list[str] | None = None,
    **kwargs,
):
    """Starts an HTTP server, serving a part of a zarr hierarchy or numpy array as zarr.

    Parameters
    ----------
    source : zarr.Array, zarr.Group, or np.ndarray
        Source data to serve over HTTP. The underlying store of a zarr.Array,
        or zarr.Group are used to forward requests. If a numpy array is provided,
        an in-memory zarray array is created, and the underlying store is wrapped.
    name : str
        Path prefix for underlying store keys (e.g. "data.zarr"). If provided, routes are
        prefixed with name.
    allowed_origins : list of str, optional
        List of allowed origins (as strings). Use wildcard "*" to allow all.
    **kwargs : keyword arguments
        All extra keyword arguments are forwarded to uvicorn.run
    """

    if isinstance(source, np.ndarray):
        # Need to cast as zarr and create store for in memory numpy array
        source = zarr.array(source)

    if not isinstance(source, (zarr.Array, zarr.Group)):
        raise TypeError(
            "Source is not one of numpy.ndarray, zarr.Array, or zarr.Group."
        )

    route = create_zarr_route(source)
    routes = [route] if name is None else [Mount("/" + name, routes=[route])]
    server = Starlette(routes=routes)
    if allowed_origins:
        server.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    uvicorn.run(server, **kwargs)
