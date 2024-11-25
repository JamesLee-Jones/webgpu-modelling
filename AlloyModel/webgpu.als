open util/relation

sig TranslationUnit {
  // TODO: global_directives: GlobalDirective
  global_decls: seq GlobalDecl
}

sig Ident {}

abstract sig GlobalDecl {}

sig FunctionDecl extends GlobalDecl {
  ident : one Ident,
  statements: seq Statement
}

// Represents a series of statments enclosed in curly braces.
sig CompoundStatement {
  // TODO: Add attribute
  statements: seq Statement
}

// Represents a statement.
abstract sig Statement {}

sig IfStatement extends Statement {
  // TODO: Add expression (condition)
}

// Each if statement is only in one place
fact {
  all if : IfStatement | lone ((FunctionDecl <: statements).if + (CompoundStatement <: statements).if)
}

run example {}
