pred nested_if_while {
	one Ident
	one TranslationUnit
	one TranslationUnit.global_decls
 	one FunctionDecl
	one IfStatement
	one WhileStatement
	Statement = IfStatement + WhileStatement
	no else_if_compound_statements
	no else_compound_statement
	WhileStatement in IfStatement.if_compound_statement.statements.elems
}