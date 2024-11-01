from inspect import signature
from typing import Any

from sqlalchemy_filter_converter.types import OperatorFunctionProtocol


def execute_operator_function(
    func: OperatorFunctionProtocol,
    a: Any,  # noqa: ANN401
    b: Any,  # noqa: ANN401
    subproduct_use: bool = False,  # noqa: FBT001, FBT002
) -> Any:  # noqa: ANN401
    """Call given operator function with checking for ``subproduct_use`` signature.

    Simple wrapper to not execute function every time with checking, that operator has
    subproduct_use.
    """
    function_signature = signature(func)
    if function_signature.parameters.get("subproduct_use"):
        return func(a, b, subproduct_use=subproduct_use)
    # function has no subproduct_use param.
    return func(a, b)
