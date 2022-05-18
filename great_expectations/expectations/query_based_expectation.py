import logging
from abc import ABC
from typing import Optional

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.exceptions.exceptions import (
    InvalidExpectationConfigurationError,
)
from great_expectations.execution_engine import (
    PandasExecutionEngine,
    SparkDFExecutionEngine,
    SqlAlchemyExecutionEngine,
)
from great_expectations.expectations.expectation import (
    ExpectationConfiguration,
    TableExpectation,
)
from great_expectations.expectations.metrics.metric_provider import (
    MetricConfiguration,
    MetricDomainTypes,
    MetricFunctionTypes,
    metric_value,
)
from great_expectations.expectations.metrics.table_metric_provider import (
    TableMetricProvider,
)
from great_expectations.expectations.registry import get_metric_kwargs
from great_expectations.expectations.util import render_evaluation_parameter_string
from great_expectations.render.renderer.renderer import renderer
from great_expectations.render.types import RenderedStringTemplateContent
from great_expectations.render.util import (
    parse_row_condition_string_pandas_engine,
    substitute_none_for_missing,
)
from great_expectations.util import camel_to_snake

logger = logging.getLogger(__name__)


class QueryMetricProvider(TableMetricProvider):
    @metric_value(engine=PandasExecutionEngine)
    def _pandas(
        cls,
        execution_engine,
        metric_domain_kwargs,
        metric_value_kwargs,
        metrics,
        runtime_configuration,
    ):
        df, _, _ = execution_engine.get_compute_domain(
            metric_domain_kwargs, domain_type=MetricDomainTypes.TABLE
        )

        breakpoint()
        return df

    @metric_value(
        engine=SqlAlchemyExecutionEngine, metric_fn_type=MetricFunctionTypes.VALUE
    )
    def _sqlalchemy(
        cls,
        execution_engine,
        metric_domain_kwargs,
        metric_value_kwargs,
        metrics,
        runtime_configuration,
    ):
        breakpoint()
        (
            selectable,
            compute_domain_kwargs,
            accessor_domain_kwargs,
        ) = execution_engine.get_compute_domain(
            metric_domain_kwargs, MetricDomainTypes.TABLE
        )

        breakpoint()

    # @metric_partial(engine=SparkDFExecutionEngine)
    # def _spark(cls, column, **kwargs):
    #     return column.isin(cls.set_)


class QueryBasedExpectation(TableExpectation, ABC):
    @staticmethod
    def register_metric(
        query_camel_name: str,
        query_: str,
    ):
        query_snake_name = camel_to_snake(query_camel_name)
        query_metric = "queried_values.match_" + query_snake_name + "_query"

        # Define the class using `type`. This allows us to name it dynamically.
        new_query_metric_provider = type(
            f"(QueriedValuesMatch{query_camel_name}Query",
            (QueryMetricProvider,),
            {
                "query_metric_name": query_metric,
                "query_": query_,
            },
        )

        return query_metric

    # def validate_configuration(self, configuration: Optional[ExpectationConfiguration]):
    #     super().validate_configuration(configuration)
    #     try:
    #         assert (
    #             getattr(self, "set_", None) is not None
    #         ), "set_ is required for SetBasedColumnMap Expectations"
    #
    #         assert (
    #             "column" in configuration.kwargs
    #         ), "'column' parameter is required for ColumnMap expectations"
    #
    #         if "mostly" in configuration.kwargs:
    #             mostly = configuration.kwargs["mostly"]
    #             assert isinstance(
    #                 mostly, (int, float)
    #             ), "'mostly' parameter must be an integer or float"
    #             assert 0 <= mostly <= 1, "'mostly' parameter must be between 0 and 1"
    #
    #     except AssertionError as e:
    #         raise InvalidExpectationConfigurationError(str(e))
    #
    #     return True

    # question, descriptive, prescriptive, diagnostic
    # @classmethod
    # @renderer(renderer_type="renderer.question")
    # def _question_renderer(
    #     cls, configuration, result=None, language=None, runtime_configuration=None
    # ):
    #     column = configuration.kwargs.get("column")
    #     mostly = configuration.kwargs.get("mostly")
    #     set_ = getattr(cls, "set_")
    #     set_semantic_name = getattr(cls, "set_semantic_name", None)
    #
    #     if mostly == 1 or mostly is None:
    #         if set_semantic_name is not None:
    #             return f'Are all values in column "{column}" in {set_semantic_name}: {str(set_)}?'
    #         else:
    #             return f'Are all values in column "{column}" in the set {str(set_)}?'
    #     else:
    #         if set_semantic_name is not None:
    #             return f'Are at least {mostly * 100}% of values in column "{column}" in {set_semantic_name}: {str(set_)}?'
    #         else:
    #             return f'Are at least {mostly * 100}% of values in column "{column}" in the set {str(set_)}?'
    #
    # @classmethod
    # @renderer(renderer_type="renderer.answer")
    # def _answer_renderer(
    #     cls, configuration=None, result=None, language=None, runtime_configuration=None
    # ):
    #     column = result.expectation_config.kwargs.get("column")
    #     mostly = result.expectation_config.kwargs.get("mostly")
    #     set_ = getattr(cls, "set_")
    #     set_semantic_name = getattr(cls, "set_semantic_name", None)
    #
    #     if result.success:
    #         if mostly == 1 or mostly is None:
    #             if set_semantic_name is not None:
    #                 return f'All values in column "{column}" are in {set_semantic_name}: {str(set_)}.'
    #             else:
    #                 return (
    #                     f'All values in column "{column}" are in the set {str(set_)}.'
    #                 )
    #         else:
    #             if set_semantic_name is not None:
    #                 return f'At least {mostly * 100}% of values in column "{column}" are in {set_semantic_name}: {str(set_)}.'
    #             else:
    #                 return f'At least {mostly * 100}% of values in column "{column}" are in the set {str(set)}.'
    #     else:
    #         if set_semantic_name is not None:
    #             return f' Less than {mostly * 100}% of values in column "{column}" are in {set_semantic_name}: {str(set_)}.'
    #         else:
    #             return f'Less than {mostly * 100}% of values in column "{column}" are in the set {str(set_)}.'
    #
    # @classmethod
    # def _atomic_prescriptive_template(
    #     cls,
    #     configuration=None,
    #     result=None,
    #     language=None,
    #     runtime_configuration=None,
    #     **kwargs,
    # ):
    #     runtime_configuration = runtime_configuration or {}
    #     include_column_name = runtime_configuration.get("include_column_name", True)
    #     include_column_name = (
    #         include_column_name if include_column_name is not None else True
    #     )
    #     styling = runtime_configuration.get("styling")
    #     params = substitute_none_for_missing(
    #         configuration.kwargs,
    #         [
    #             "column",
    #             "set_",
    #             "mostly",
    #             "row_condition",
    #             "condition_parser",
    #             "set_semantic_name",
    #         ],
    #     )
    #     params_with_json_schema = {
    #         "column": {"schema": {"type": "string"}, "value": params.get("column")},
    #         "mostly": {"schema": {"type": "number"}, "value": params.get("mostly")},
    #         "mostly_pct": {
    #             "schema": {"type": "number"},
    #             "value": params.get("mostly_pct"),
    #         },
    #         "set_": {"schema": {"type": "string"}, "value": params.get("set_")},
    #         "row_condition": {
    #             "schema": {"type": "string"},
    #             "value": params.get("row_condition"),
    #         },
    #         "condition_parser": {
    #             "schema": {"type": "string"},
    #             "value": params.get("condition_parser"),
    #         },
    #         "set_semantic_name": {
    #             "schema": {"type": "string"},
    #             "value": params.get("set_semantic_name"),
    #         },
    #     }
    #
    #     if not params.get("set_"):
    #         template_str = "values must match a set but none was specified."
    #     else:
    #         if params.get("set_semantic_name"):
    #             template_str = "values must match the set $set_semantic_name: $set_"
    #         else:
    #             template_str = "values must match this set: $set_"
    #         if params["mostly"] is not None:
    #             params_with_json_schema["mostly_pct"]["value"] = num_to_str(
    #                 params["mostly"] * 100, precision=15, no_scientific=True
    #             )
    #             template_str += ", at least $mostly_pct % of the time."
    #         else:
    #             template_str += "."
    #
    #     if include_column_name:
    #         template_str = "$column " + template_str
    #
    #     if params["row_condition"] is not None:
    #         (
    #             conditional_template_str,
    #             conditional_params,
    #         ) = parse_row_condition_string_pandas_engine(
    #             params["row_condition"], with_schema=True
    #         )
    #         template_str = conditional_template_str + ", then " + template_str
    #         params_with_json_schema.update(conditional_params)
    #
    #     return (template_str, params_with_json_schema, styling)
    #
    # @classmethod
    # @renderer(renderer_type="renderer.prescriptive")
    # @render_evaluation_parameter_string
    # def _prescriptive_renderer(
    #     cls,
    #     configuration=None,
    #     result=None,
    #     language=None,
    #     runtime_configuration=None,
    #     **kwargs,
    # ):
    #     runtime_configuration = runtime_configuration or {}
    #     include_column_name = runtime_configuration.get("include_column_name", True)
    #     include_column_name = (
    #         include_column_name if include_column_name is not None else True
    #     )
    #     styling = runtime_configuration.get("styling")
    #     params = substitute_none_for_missing(
    #         configuration.kwargs,
    #         [
    #             "column",
    #             "set_",
    #             "mostly",
    #             "row_condition",
    #             "condition_parser",
    #             "set_semantic_name",
    #         ],
    #     )
    #
    #     if not params.get("set_"):
    #         template_str = "values must match a set but none was specified."
    #     else:
    #         if params.get("set_semantic_name"):
    #             template_str = "values must match the set $set_semantic_name: $set_"
    #         else:
    #             template_str = "values must match this set: $set_"
    #         if params["mostly"] is not None:
    #             params["mostly_pct"] = num_to_str(
    #                 params["mostly"] * 100, precision=15, no_scientific=True
    #             )
    #             template_str += ", at least $mostly_pct % of the time."
    #         else:
    #             template_str += "."
    #
    #     if include_column_name:
    #         template_str = "$column " + template_str
    #
    #     if params["row_condition"] is not None:
    #         (
    #             conditional_template_str,
    #             conditional_params,
    #         ) = parse_row_condition_string_pandas_engine(params["row_condition"])
    #         template_str = conditional_template_str + ", then " + template_str
    #         params.update(conditional_params)
    #
    #     params_with_json_schema = {
    #         "column": {"schema": {"type": "string"}, "value": params.get("column")},
    #         "mostly": {"schema": {"type": "number"}, "value": params.get("mostly")},
    #         "mostly_pct": {
    #             "schema": {"type": "number"},
    #             "value": params.get("mostly_pct"),
    #         },
    #         "set_": {"schema": {"type": "string"}, "value": params.get("set_")},
    #         "row_condition": {
    #             "schema": {"type": "string"},
    #             "value": params.get("row_condition"),
    #         },
    #         "condition_parser": {
    #             "schema": {"type": "string"},
    #             "value": params.get("condition_parser"),
    #         },
    #         "set_semantic_name": {
    #             "schema": {"type": "string"},
    #             "value": params.get("set_semantic_name"),
    #         },
    #     }
    #
    #     return [
    #         RenderedStringTemplateContent(
    #             **{
    #                 "content_block_type": "string_template",
    #                 "string_template": {
    #                     "template": template_str,
    #                     "params": params,
    #                     "styling": styling,
    #                 },
    #             }
    #         )
    #     ]