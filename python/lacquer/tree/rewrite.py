class ExpressionRewriter(object):
    def __init__(self, line=None, pos=None):
        self.line = line
        self.pos = pos

    def rewrite_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_row(self, node, context, tree_rewriter):
        pass

    def rewrite_arithmetic_unary(self, node, context, tree_rewriter):
        pass

    def rewrite_arithmetic_binary(self, node, context, tree_rewriter):
        pass

    def rewrite_comparison_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_between_predicate(self, node, context, tree_rewriter):
        pass

    def rewrite_logical_binary_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_not_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_is_null_predicate(self, node, context, tree_rewriter):
        pass

    def rewrite_is_not_null_predicate(self, node, context, tree_rewriter):
        pass

    def rewrite_null_if_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_if_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_searched_case_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_simple_case_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_when_clause(self, node, context, tree_rewriter):
        pass

    def rewrite_coalesce_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_in_list_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_function_call(self, node, context, tree_rewriter):
        pass

    def rewrite_lambda_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_like_predicate(self, node, context, tree_rewriter):
        pass

    def rewrite_in_predicate(self, node, context, tree_rewriter):
        pass

    def rewrite_subquery_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_literal(self, node, context, tree_rewriter):
        pass

    def rewrite_array_constructor(self, node, context, tree_rewriter):
        pass

    def rewrite_subscript_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_qualified_name_reference(self, node, context, tree_rewriter):
        pass

    def rewrite_dereference_expression(self, node, context, tree_rewriter):
        pass

    def rewrite_extract(self, node, context, tree_rewriter):
        pass

    def rewrite_current_time(self, node, context, tree_rewriter):
        pass

    def rewrite_cast(self, node, context, tree_rewriter):
        pass


class ExpressionTreeRewriter(object):
    def __init__(self, line=None, pos=None, rewriter=None, visitor=None):
        self.line = line
        self.pos = pos
        self.rewriter = rewriter
        self.visitor = visitor

    def rewrite_with(self, rewriter, node, context=None):
        pass

    def rewrite(self, node, context):
        pass

    def default_rewrite(self, node, context):
        pass

    def same_elements(self, a, b):
        pass
