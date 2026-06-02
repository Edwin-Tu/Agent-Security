from token_guard.token_expander import TokenExpander as _RealTokenExpander


class TokenExpander:
	def __init__(self, rule_path: str | None = None):
		# legacy compatibility wrapper: ignore rule_path
		self._inner = _RealTokenExpander()

	def expand(self, assets):
		return self._inner.expand(assets)

	@property
	def restricted_tokens(self):
		return self._inner.restricted_tokens

__all__ = ["TokenExpander"]
