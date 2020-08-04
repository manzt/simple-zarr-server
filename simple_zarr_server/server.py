import numpy as np
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware

import uvicorn
import zarr


def create_zarr_server(z):
    """Creates a Starlette app, mapping HTTP requests on top of a Zarr store.

    Parameters
    ----------
    z : zarr.Array or zarr.Group
        Part of zarr hierarchy to expose over HTTP. The `read_only` property is
        checked to determine which HTTP methods are available.

    Returns
    -------
    app : starlette.applications.Starlette
        Starlette app
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
            except:
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

    routes = [Route("/{path:path}", endpoint=map_request, methods=methods)]
    return Starlette(routes=routes)


def serve(source, *, allowed_origins=None, **kwargs):
    """Starts an HTTP server, serving a part of a zarr hierarchy or numpy array as zarr.

    Parameters
    ----------
    source : zarr.Array, zarr.Group, or np.ndarray
        Source data to serve over HTTP. The underlying store of a zarr.Array,
        or zarr.Group are used to forward requests. If a numpy array is provided,
        an in-memory zarry array is created, and the underlying store is wrapped.
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

    server = create_zarr_server(source)
    if allowed_origins:
        server.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    uvicorn.run(server, **kwargs)
