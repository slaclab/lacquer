
class AstVisitor(object):
    def __init__(self, line=None, pos=None):
        self.line = line
        self.pos = pos

    def process(self, node, context):
        return node.accept(self, context)

    def visit_node(self, node, context):
        return None

    def visit_expression(self, node, context):
        return self.visit_node(node, context)

    def visit_reset_session(self, node, context):
        return self.visit_statement(node, context)

    def visit_current_time(self, node, context):
        return self.visit_expression(node, context)

    def visit_extract(self, node, context):
        return self.visit_expression(node, context)

    def visit_arithmetic_binary(self, node, context):
        return self.visit_expression(node, context)

    def visit_between_predicate(self, node, context):
        return self.visit_expression(node, context)

    def visit_coalesce_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_comparison_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_literal(self, node, context):
        return self.visit_expression(node, context)

    def visit_double_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_statement(self, node, context):
        return self.visit_node(node, context)

    def visit_query(self, node, context):
        return self.visit_statement(node, context)

    def visit_explain(self, node, context):
        return self.visit_statement(node, context)

    def visit_show_tables(self, node, context):
        return self.visit_statement(node, context)

    def visit_show_schemas(self, node, context):
        return self.visit_statement(node, context)

    def visit_show_catalogs(self, node, context):
        return self.visit_statement(node, context)

    def visit_show_columns(self, node, context):
        return self.visit_statement(node, context)

    def visit_show_partitions(self, node, context):
        return self.visit_statement(node, context)

    def visit_show_functions(self, node, context):
        return self.visit_statement(node, context)

    def visit_use(self, node, context):
        return self.visit_statement(node, context)

    def visit_show_session(self, node, context):
        return self.visit_statement(node, context)

    def visit_set_session(self, node, context):
        return self.visit_statement(node, context)

    def visit_generic_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_time_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_explain_option(self, node, context):
        return self.visit_node(node, context)

    def visit_with(self, node, context):
        return self.visit_node(node, context)

    def visit_approximate(self, node, context):
        return self.visit_node(node, context)

    def visit_with_query(self, node, context):
        return self.visit_node(node, context)

    def visit_select(self, node, context):
        return self.visit_node(node, context)

    def visit_relation(self, node, context):
        return self.visit_node(node, context)

    def visit_query_body(self, node, context):
        return self.visit_relation(node, context)

    def visit_query_specification(self, node, context):
        return self.visit_query_body(node, context)

    def visit_set_operation(self, node, context):
        return self.visit_query_body(node, context)

    def visit_union(self, node, context):
        return self.visit_set_operation(node, context)

    def visit_intersect(self, node, context):
        return self.visit_set_operation(node, context)

    def visit_except(self, node, context):
        return self.visit_set_operation(node, context)

    def visit_timestamp_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_when_clause(self, node, context):
        return self.visit_expression(node, context)

    def visit_interval_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_in_predicate(self, node, context):
        return self.visit_expression(node, context)

    def visit_function_call(self, node, context):
        return self.visit_expression(node, context)

    def visit_lambda_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_simple_case_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_string_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_binary_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_boolean_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_in_list_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_qualified_name_reference(self, node, context):
        return self.visit_expression(node, context)

    def visit_dereference_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_null_if_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_if_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_null_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_arithmetic_unary(self, node, context):
        return self.visit_expression(node, context)

    def visit_not_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_select_item(self, node, context):
        return self.visit_node(node, context)

    def visit_single_column(self, node, context):
        return self.visit_select_item(node, context)

    def visit_all_columns(self, node, context):
        return self.visit_select_item(node, context)

    def visit_searched_case_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_like_predicate(self, node, context):
        return self.visit_expression(node, context)

    def visit_is_not_null_predicate(self, node, context):
        return self.visit_expression(node, context)

    def visit_is_null_predicate(self, node, context):
        return self.visit_expression(node, context)

    def visit_array_constructor(self, node, context):
        return self.visit_expression(node, context)

    def visit_subscript_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_long_literal(self, node, context):
        return self.visit_literal(node, context)

    def visit_logical_binary_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_subquery_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_sort_item(self, node, context):
        return self.visit_node(node, context)

    def visit_table(self, node, context):
        return self.visit_query_body(node, context)

    def visit_unnest(self, node, context):
        return self.visit_relation(node, context)

    def visit_values(self, node, context):
        return self.visit_query_body(node, context)

    def visit_row(self, node, context):
        return self.visit_node(node, context)

    def visit_table_subquery(self, node, context):
        return self.visit_query_body(node, context)

    def visit_aliased_relation(self, node, context):
        return self.visit_relation(node, context)

    def visit_sampled_relation(self, node, context):
        return self.visit_relation(node, context)

    def visit_join(self, node, context):
        return self.visit_relation(node, context)

    def visit_exists(self, node, context):
        return self.visit_expression(node, context)

    def visit_try_expression(self, node, context):
        return self.visit_expression(node, context)

    def visit_cast(self, node, context):
        return self.visit_expression(node, context)

    def visit_input_reference(self, node, context):
        return self.visit_expression(node, context)

    def visit_window(self, node, context):
        return self.visit_node(node, context)

    def visit_window_frame(self, node, context):
        return self.visit_node(node, context)

    def visit_frame_bound(self, node, context):
        return self.visit_node(node, context)

    def visit_call_argument(self, node, context):
        return self.visit_node(node, context)

    def visit_table_element(self, node, context):
        return self.visit_node(node, context)

    def visit_create_table(self, node, context):
        return self.visit_statement(node, context)

    def visit_create_table_as_select(self, node, context):
        return self.visit_statement(node, context)

    def visit_drop_table(self, node, context):
        return self.visit_statement(node, context)

    def visit_rename_table(self, node, context):
        return self.visit_statement(node, context)

    def visit_rename_column(self, node, context):
        return self.visit_statement(node, context)

    def visit_add_column(self, node, context):
        return self.visit_statement(node, context)

    def visit_create_view(self, node, context):
        return self.visit_statement(node, context)

    def visit_drop_view(self, node, context):
        return self.visit_statement(node, context)

    def visit_insert(self, node, context):
        return self.visit_node(node, context)

    def visit_call(self, node, context):
        return self.visit_node(node, context)

    def visit_delete(self, node, context):
        return self.visit_statement(node, context)

    def visit_start_transaction(self, node, context):
        return self.visit_statement(node, context)

    def visit_grant(self, node, context):
        return self.visit_statement(node, context)

    def visit_transaction_mode(self, node, context):
        return self.visit_node(node, context)

    def visit_isolation_level(self, node, context):
        return self.visit_transaction_mode(node, context)

    def visit_transaction_access_mode(self, node, context):
        return self.visit_transaction_mode(node, context)

    def visit_commit(self, node, context):
        return self.visit_statement(node, context)

    def visit_rollback(self, node, context):
        return self.visit_statement(node, context)

    def visit_at_time_zone(self, node, context):
        return self.visit_expression(node, context)


class DefaultTraversalVisitor(AstVisitor):
    def __init__(self, line=None, pos=None):
        super(DefaultTraversalVisitor, self).__init__(line, pos)

    def visit_extract(self, node, context):
        pass

    def visit_cast(self, node, context):
        pass

    def visit_arithmetic_binary(self, node, context):
        pass

    def visit_between_predicate(self, node, context):
        pass

    def visit_coalesce_expression(self, node, context):
        pass

    def visit_array_constructor(self, node, context):
        pass

    def visit_subscript_expression(self, node, context):
        pass

    def visit_comparison_expression(self, node, context):
        pass

    def visit_query(self, node, context):
        pass

    def visit_with(self, node, context):
        pass

    def visit_with_query(self, node, context):
        pass

    def visit_select(self, node, context):
        pass

    def visit_single_column(self, node, context):
        pass

    def visit_when_clause(self, node, context):
        pass

    def visit_in_predicate(self, node, context):
        pass

    def visit_function_call(self, node, context):
        pass

    def visit_dereference_expression(self, node, context):
        pass

    def visit_window(self, node, context):
        pass

    def visit_window_frame(self, node, context):
        pass

    def visit_frame_bound(self, node, context):
        pass

    def visit_simple_case_expression(self, node, context):
        pass

    def visit_in_list_expression(self, node, context):
        pass

    def visit_null_if_expression(self, node, context):
        pass

    def visit_if_expression(self, node, context):
        pass

    def visit_arithmetic_unary(self, node, context):
        pass

    def visit_not_expression(self, node, context):
        pass

    def visit_searched_case_expression(self, node, context):
        pass

    def visit_like_predicate(self, node, context):
        pass

    def visit_is_not_null_predicate(self, node, context):
        pass

    def visit_is_null_predicate(self, node, context):
        pass

    def visit_logical_binary_expression(self, node, context):
        pass

    def visit_subquery_expression(self, node, context):
        pass

    def visit_sort_item(self, node, context):
        pass

    def visit_query_specification(self, node, context):
        pass

    def visit_union(self, node, context):
        pass

    def visit_intersect(self, node, context):
        pass

    def visit_except(self, node, context):
        pass

    def visit_values(self, node, context):
        pass

    def visit_row(self, node, context):
        pass

    def visit_table_subquery(self, node, context):
        pass

    def visit_aliased_relation(self, node, context):
        pass

    def visit_sampled_relation(self, node, context):
        pass

    def visit_join(self, node, context):
        pass

    def visit_unnest(self, node, context):
        pass


class DefaultExpressionTraversalVisitor(DefaultTraversalVisitor):
    def __init__(self, line=None, pos=None):
        super(DefaultExpressionTraversalVisitor, self).__init__(line, pos)

    def visit_subquery_expression(self, node, context):
        return None


class StackableAstVisitor(AstVisitor):
    def __init__(self, line=None, pos=None):
        super(StackableAstVisitor, self).__init__(line, pos)

    def process(self, node, context):
        pass
