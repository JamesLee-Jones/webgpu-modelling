open util/relation

some sig TranslationUnit {
  // TODO: global_directives: GlobalDirective
  global_decls: seq GlobalDecl
}

sig Ident {}

// Every identifier belongs to something
fact {
  all i : Ident | one (FunctionDecl <: ident).i + (VariableDecl <: ident).i
}

------------------------------------- Global Declerations -------------------------------------

abstract sig GlobalDecl {}

sig FunctionDecl extends GlobalDecl {
  ident : one Ident,
  // TODO: Add param_list
  compound_statement: one CompoundStatement
}

// Each function decl is only in one translation unit
fact {
  all f : FunctionDecl | one global_decls.f
}

// Each function decl has a uniq ident
// TODO: Change this to only apply within a translation unit
fact {
  all disj f, g : FunctionDecl | f.ident != g.ident
}


sig GlobalVarDecl extends GlobalDecl {
  variable_decl: one VariableDecl,
  expression: lone Expression
}

// Each global variable decleration is only in one translation unit
fact {
  all gvd: GlobalVarDecl | one global_decls.gvd
}

sig VariableDecl {
  ident: one Ident
}

// Each VariableDecl is only in one GlobalVarDecl
fact {
  all vd: VariableDecl | one variable_decl.vd
}

sig Expression {}

// Each expression is part of something
fact {
  all e: Expression | one expression.e
}

------------------------------------- Compound Statement -------------------------------------

// Represents a series of statments enclosed in curly braces.
sig CompoundStatement {
  // TODO: Add attribute
  statements: seq Statement
}

// Each CompoundStatement is only in one place
fact {
  all c : CompoundStatement | 
    one (FunctionDecl <: compound_statement).c +
           (WhileStatement <: compound_statement).c +
           (IfStatement <: if_compound_statement).c +
           (IfStatement <: else_compound_statement).c +
           univ.(IfStatement <: else_if_compound_statements).c
}

// Prevent compound statements from indirectly being their own parents.
fact {
  all c : CompoundStatement |
     c -> c not in ^(reachableCompoundStatements)
}

// Map compound statements to the compound statements they contain.
fun reachableCompoundStatements : CompoundStatement -> CompoundStatement {
  { c1 : CompoundStatement, c2 : CompoundStatement | c2 in childCompoundStatements[c1]}
}

// Get the set of compound statements reachable from some parent compound statement.
fun childCompoundStatements[c : one CompoundStatement] : CompoundStatement {
  let s = c.statements.elems |  // Get the statements in the compound statement.
    (s <: IfStatement).(if_compound_statement + else_compound_statement) +
    (s <: IfStatement).else_if_compound_statements.elems +
    (s <: WhileStatement).compound_statement 
}

------------------------------------------------------------------------------------------
------------------------------------- Statement -------------------------------------
------------------------------------------------------------------------------------------

// Represents a statement.
abstract sig Statement {}

// There is only one instance of each Statement.
fact {
  all s : Statement | one statements.s
}

------------------------------------- IfStatement -------------------------------------

sig IfStatement extends Statement {
  // TODO: Add expression (condition)
  if_compound_statement: one CompoundStatement,
  else_if_compound_statements: seq CompoundStatement,
  else_compound_statement: lone CompoundStatement
}

// Each compound statement is only in one if branch, this is implicit
// in the grammar as it's impossible to write a program violating it.
fact {
  // TODO: How can this be more cleanly expressed?
  all c : CompoundStatement |
     (lone if_compound_statement.c and no else_if_compound_statements.c and no else_compound_statement.c)
     or (no if_compound_statement.c and lone else_if_compound_statements.c and no else_compound_statement.c)
     or (no if_compound_statement.c and no else_if_compound_statements.c and lone else_compound_statement.c)
}

------------------------------------- WhileStatement -------------------------------------

sig WhileStatement extends Statement {
  // TODO: Add expression (condition)
  compound_statement: CompoundStatement
}

run example {
	some GlobalVarDecl
	some FunctionDecl
	some IfStatement
    some else_if_compound_statements
	some WhileStatement
} for 20 but 1 TranslationUnit
