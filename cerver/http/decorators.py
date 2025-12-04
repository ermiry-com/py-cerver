"""Groups of routes with decorators, and the callbacks of the handlers and the middlewares."""

from typing import Any, Callable

from ..callbacks import callbacks, callback_keep, callback_wrap
from ..lib import lib_c_string

from .middleware import HttpBeforeMiddleware, HttpAfterMiddleware
from .requests.methods import REQUEST_METHOD_GET, REQUEST_METHOD_HEAD, REQUEST_METHOD_POST
from .requests.methods import REQUEST_METHOD_PUT, REQUEST_METHOD_PATCH, REQUEST_METHOD_DELETE
from .requests.methods import REQUEST_METHOD_OPTIONS
from .routes import HttpHandler
from .tree import http_cerver_group_create, http_group_create, http_group_route_add
from .tree import http_group_root_add
from .tree import http_group_add_before, http_group_add_after
from .tree import http_endpoint_set_modifier, http_endpoint_set_auth
from .tree import http_endpoint_set_max_body_size, http_endpoint_set_cors
from .tree import http_endpoint_set_etag, http_endpoint_set_compression
from .tree import http_endpoint_set_authentication_with_body
from .tree import http_endpoint_add_before, http_endpoint_add_after

__all__ = [
	"http_callbacks", "http_callback_keep", "http_callback_wrap",
	"http_handler", "http_before_middleware", "http_after_middleware",
	"http_endpoint_configure", "http_group_root_check",
	"HttpGroup", "http_group"
]

# the kept callbacks, shared with the rest of the package (cerver.callbacks)
http_callbacks = callbacks
http_callback_keep = callback_keep
http_callback_wrap = callback_wrap

def http_handler (function: Callable) -> HttpHandler:
	"""Returns a function as a kept HttpHandler.

	Args:
		function: A Python function (http_receive, request), or an HttpHandler.

	Returns:
		The HttpHandler, kept for as long as the process lives.
	"""
	return callback_wrap (function, HttpHandler)

def http_before_middleware (function: Callable) -> HttpBeforeMiddleware:
	"""Returns a function as a kept HttpBeforeMiddleware.

	Args:
		function: A Python function (http_receive, request) that returns an HTTP_MIDDLEWARE_RESULT_*.

	Returns:
		The HttpBeforeMiddleware.
	"""
	return callback_wrap (function, HttpBeforeMiddleware)

def http_after_middleware (function: Callable) -> HttpAfterMiddleware:
	"""Returns a function as a kept HttpAfterMiddleware.

	Args:
		function: A Python function (http_receive, request).

	Returns:
		The HttpAfterMiddleware.
	"""
	return callback_wrap (function, HttpAfterMiddleware)

def http_endpoint_configure (
	endpoint: int,
	modifier: int | None = None, auth: int | None = None,
	max_body_size: int | None = None, cors: bool | None = None,
	authentication_with_body: bool | None = None,
	etag: bool | None = None, compression: bool | None = None,
	before: tuple = (), after: tuple = ()
) -> None:
	"""Sets the settings of an endpoint that were given, the others are inherited from its groups.

	Args:
		endpoint: The HttpEndpoint.
		modifier: An HTTP_ROUTE_MODIFIER_* value.
		auth: An HTTP_ROUTE_AUTH_TYPE_* value.
		max_body_size: The biggest body in bytes.
		cors: True to add Access-Control-Allow-Origin.
		authentication_with_body: True to authenticate after the body was received.
		etag: True to add a strong ETag.
		compression: True to compress with gzip.
		before: Python functions that run before the handler.
		after: Python functions that run after the handler.
	"""
	settings = (
		(modifier, http_endpoint_set_modifier),
		(auth, http_endpoint_set_auth),
		(max_body_size, http_endpoint_set_max_body_size),
		(cors, http_endpoint_set_cors),
		(authentication_with_body, http_endpoint_set_authentication_with_body),
		(etag, http_endpoint_set_etag),
		(compression, http_endpoint_set_compression)
	)

	for value, setter in settings:
		if (value is not None):
			setter (endpoint, value)

	for middleware in before:
		http_endpoint_add_before (endpoint, http_before_middleware (middleware))

	for middleware in after:
		http_endpoint_add_after (endpoint, http_after_middleware (middleware))

def http_group_root_check (method: int | None, handler: Callable | None) -> None:
	"""Checks the endpoint of a group itself.

	Args:
		method: A REQUEST_METHOD_* value, or None.
		handler: The handler, or None.

	Raises:
		ValueError: If there is a method without a handler or a handler without a method.
	"""
	if ((method is None) != (handler is None)):
		raise ValueError ("The root of a group needs both its method and its handler")

class HttpGroup:
	"""A group of routes with decorators.

	Example:
		api = HttpGroup.create (http_cerver, "api/items")

		@api.get ("/:id<objectid>")
		def item_handler (http_receive, request):
			...

	The handlers keep their signature (http_receive, request) and each decorator returns
	the HttpHandler that was registered.

	Attributes:
		group: The HttpGroup of cerver.
	"""

	def __init__ (self, group: int):
		"""Wraps a group of cerver.

		Args:
			group: The HttpGroup.

		Raises:
			ValueError: If the group is None (cerver could not create it).
		"""
		if (not group):
			raise ValueError ("Failed to create the HTTP group, see the routes error of the cerver")

		self.group = group

	@classmethod
	def create (
		cls, http_cerver: int, prefix: str | None = None,
		method: int | None = None, handler: Callable | None = None, **settings
	) -> "HttpGroup":
		"""Creates a top level group, with the endpoint of the group itself when there is a handler.

		Args:
			http_cerver: The HttpCerver.
			prefix: The prefix of its paths, None for the root.
			method: The method of the endpoint of the group, like REQUEST_METHOD_GET.
			handler: The handler of the endpoint of the group.
			**settings: The settings of that endpoint (see http_endpoint_configure ()).

		Returns:
			The group.

		Raises:
			ValueError: If the group could not be created or its root is incomplete.
		"""
		# the root is checked before the group is created, so an error leaves no group in the cerver
		http_group_root_check (method, handler)

		group = cls (http_cerver_group_create (http_cerver, lib_c_string (prefix)))

		group.root_set (method, handler, **settings)

		return group

	def subgroup (
		self, prefix: str,
		method: int | None = None, handler: Callable | None = None, **settings
	) -> "HttpGroup":
		"""Creates a group inside this one, with the endpoint of the group itself when there is a handler.

		Args:
			prefix: The prefix relative to this group.
			method: The method of the endpoint of the group.
			handler: The handler of the endpoint of the group.
			**settings: The settings of that endpoint.

		Returns:
			The group.
		"""
		http_group_root_check (method, handler)

		group = HttpGroup (http_group_create (self.group, lib_c_string (prefix)))

		group.root_set (method, handler, **settings)

		return group

	def root (self, method: int, handler: Callable, **settings) -> int | None:
		"""Adds the handler as the endpoint of the method in the path of the group itself.

		Args:
			method: A REQUEST_METHOD_* value.
			handler: The handler.
			**settings: The settings of the endpoint.

		Returns:
			The HttpEndpoint, None on error (the cerver will not start).
		"""
		endpoint = http_group_root_add (self.group, method, http_handler (handler))

		if (endpoint):
			http_endpoint_configure (endpoint, **settings)

		return endpoint

	def root_set (self, method: int | None, handler: Callable | None, **settings) -> None:
		"""Adds the endpoint of the group itself if there is a handler.

		Args:
			method: A REQUEST_METHOD_* value, or None.
			handler: The handler, or None.
			**settings: The settings of the endpoint.

		Raises:
			ValueError: If there is a method without a handler or a handler without a method.
		"""
		http_group_root_check (method, handler)

		if (handler is not None):
			self.root (method, handler, **settings)

	def add (self, method: int, path: str, handler: Callable, **settings) -> int | None:
		"""Adds the handler as the endpoint of the method in a path relative to the group.

		Args:
			method: A REQUEST_METHOD_* value.
			path: The path, like "/:id<objectid>".
			handler: The handler.
			**settings: The settings of the endpoint.

		Returns:
			The HttpEndpoint, None on error (the cerver will not start).
		"""
		endpoint = http_group_route_add (self.group, method, lib_c_string (path), http_handler (handler))

		if (endpoint):
			http_endpoint_configure (endpoint, **settings)

		return endpoint

	def route (self, method: int, path: str, **settings) -> Callable [[Callable], Any]:
		"""Returns a decorator that adds the function as the endpoint of a method and a path.

		Args:
			method: A REQUEST_METHOD_* value.
			path: The path relative to the group.
			**settings: The settings of the endpoint.

		Returns:
			The decorator, it returns the registered HttpHandler.
		"""
		def decorator (function: Callable) -> HttpHandler:
			handler = http_handler (function)
			self.add (method, path, handler, **settings)
			return handler

		return decorator

	def get (self, path: str, **settings) -> Callable:
		"""Returns a decorator of a GET endpoint, see route ()."""
		return self.route (REQUEST_METHOD_GET, path, **settings)

	def head (self, path: str, **settings) -> Callable:
		"""Returns a decorator of a HEAD endpoint, a GET one already answers HEAD."""
		return self.route (REQUEST_METHOD_HEAD, path, **settings)

	def post (self, path: str, **settings) -> Callable:
		"""Returns a decorator of a POST endpoint, see route ()."""
		return self.route (REQUEST_METHOD_POST, path, **settings)

	def put (self, path: str, **settings) -> Callable:
		"""Returns a decorator of a PUT endpoint, see route ()."""
		return self.route (REQUEST_METHOD_PUT, path, **settings)

	def patch (self, path: str, **settings) -> Callable:
		"""Returns a decorator of a PATCH endpoint, see route ()."""
		return self.route (REQUEST_METHOD_PATCH, path, **settings)

	def delete (self, path: str, **settings) -> Callable:
		"""Returns a decorator of a DELETE endpoint, see route ()."""
		return self.route (REQUEST_METHOD_DELETE, path, **settings)

	def options (self, path: str, **settings) -> Callable:
		"""Returns a decorator of an OPTIONS endpoint, cerver answers OPTIONS by itself otherwise."""
		return self.route (REQUEST_METHOD_OPTIONS, path, **settings)

	def before (self, function: Callable) -> HttpBeforeMiddleware:
		"""Adds a middleware that runs before the handlers of the group, usable as a decorator.

		Args:
			function: A Python function (http_receive, request) that returns an HTTP_MIDDLEWARE_RESULT_*.

		Returns:
			The HttpBeforeMiddleware.
		"""
		middleware = http_before_middleware (function)
		http_group_add_before (self.group, middleware)
		return middleware

	def after (self, function: Callable) -> HttpAfterMiddleware:
		"""Adds a middleware that runs after the handlers of the group, usable as a decorator.

		Args:
			function: A Python function (http_receive, request).

		Returns:
			The HttpAfterMiddleware.
		"""
		middleware = http_after_middleware (function)
		http_group_add_after (self.group, middleware)
		return middleware

def http_group (
	http_cerver: int, prefix: str | None = None,
	method: int | None = None, handler: Callable | None = None, **settings
) -> HttpGroup:
	"""Creates a top level group, see HttpGroup.create ().

	Args:
		http_cerver: The HttpCerver.
		prefix: The prefix of its paths, None for the root.
		method: The method of the endpoint of the group.
		handler: The handler of the endpoint of the group.
		**settings: The settings of that endpoint.

	Returns:
		The group.
	"""
	return HttpGroup.create (http_cerver, prefix, method, handler, **settings)
