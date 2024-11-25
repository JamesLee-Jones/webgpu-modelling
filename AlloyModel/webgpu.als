open util/relation

some sig TranslationUnit {
  // TODO: global_directives: GlobalDirective
  global_decls: seq GlobalDecl
}

sig Ident {}

// Every identifier belongs to something
fact {
  all i : Ident | lone (FunctionDecl <: ident).i + (VariableDecl <: ident).i
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

// Represents a series of statments enclosed in curly braces.
sig CompoundStatement {
  // TODO: Add attribute
  statements: seq Statement
}

// Each CompoundStatement is only in one place
fact {
  all c : CompoundStatement | one compound_statement.c
}

// Represents a statement.
abstract sig Statement {}

sig IfStatement extends Statement {
  // TODO: Add expression (condition)
}

// Each if statement is only in one place
fact {
  all if : IfStatement | one statements.if
}

run example {}
