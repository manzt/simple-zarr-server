import numpy as np
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
import uvicorn
import zarr


def create_zarr_server(store, writeable=False):
    """Creates a Starlette app, mapping HTTP requests on top of a Zarr store.

    Parameters
    ----------
    store : collections.MutableMapping
        Mutable interface underlying a zarr.Array or zarr.Group.
    writeable : bool
        Whether to allow write to store over HTTP.

    Returns
    -------
    app : starlette.applications.Starlette
        Starlette app
    """

    async def map_request(request):
        path = request.path_params["path"]
        if request.method == "PUT":
            # PUT only handled if writeable
            try:
                blob = await request.body()
                store[path] = blob
                return Response(status_code=200)
            except:
                return Response(status_code=404)
        else:
            try:
                # Return blob if GET, otherwise it's HEAD and should return empty body
                body = store[path]
                if request.method == "HEAD":
                    body = None
                return Response(body, status_code=200)
            except KeyError:
                # Key not in store, return 404
                return Response(status_code=404)

    methods = ["GET", "HEAD", "PUT"] if writeable else ["GET", "HEAD"]
    routes = [Route("/{path:path}", endpoint=map_request, methods=methods)]
    return Starlette(routes=routes)


def serve(source, *, writeable=False, **kwargs):
    """Starts an HTTP server, serving a part of a zarr hierarchy or numpy array as zarr.

    Parameters
    ----------
    source : zarr.Array, zarr.Group, or np.ndarray
        Source data to serve over HTTP. The underlying store of a zarr.Array,
        or zarr.Group are used to forward requests. If a numpy array is provided,
        an in-memory zarry array is created, and the underlying store is wrapped.
    writeable : bool
        Whether to allow write to store over HTTP.
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

    server = create_zarr_server(source.store, writeable)
    uvicorn.run(server, **kwargs)
