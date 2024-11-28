import sys
import xml.etree.ElementTree as elementTree
from typing import Set, List


label_to_id_dict = None
indent = 0

def get_sig_from_instance(instance, label: str):
    for child in instance:
        if child.tag == "sig" and child.attrib["label"].endswith(label):
            return child

    assert False  # This should never happen

def get_field_from_instance(instance, label: str = None, id: int = None, parent_id: int = None):
    for child in instance:
        if (child.tag == "field" and
                (not label or get_label(child).endswith(label)) and
                (not id or get_id(child) == id) and
                (not parent_id or get_parent_id(child) == parent_id)):
            return child

    assert False  # This should never happen


def get_atoms_from_sig(sig) -> Set:
    result = set()
    for child in sig:
        if child.tag == "atom":
            result.add(child)

    return result


def find_tuples_by_key(instance, label: str):
    result = []
    for child in instance:
        if child.tag == "tuple" and child[0].tag == "atom" and child[0].attrib["label"].endswith(label):
            tuple = []
            for atom in child:
                tuple.append(atom.attrib["label"])
            result.append(tuple)

    return result


def get_label(node):
    return node.attrib["label"]


def get_id(node) -> int:
    return int(node.attrib["ID"])


def get_parent_id(node) -> int:
    return int(node.attrib["parentID"])


def ident_to_label(ident: str) -> str:
    return ident.split("$")[0]


def ident_to_name(ident: str) -> str:
    return ident.replace("$", "")


def get_id_from_ident(identifier) -> int:
    label = ident_to_label(identifier)
    if label in label_to_id_dict:
        return label_to_id_dict[label]
    if ('this/' + label) in label_to_id_dict:
        return label_to_id_dict['this/' + label]
    assert False


def get_translation_units(instance) -> Set:
    # Find the translation unit signature and get a list of all translation units
    translation_unit_sig = get_sig_from_instance(instance, "this/TranslationUnit")
    translation_units = get_atoms_from_sig(translation_unit_sig)
    return translation_units


def get_global_decls_in_translation_unit(instance, translation_unit) -> List[List]:
    # Get the global decls for the current translation unit.
    global_decls_field = get_field_from_instance(instance, "global_decls")
    global_decl_tuples = find_tuples_by_key(global_decls_field, get_label(translation_unit))
    return global_decl_tuples


def generate_label_to_id_dict(instance):
    result = {}
    for child in instance:
        if child.tag == "sig" or child.tag == "field":
            result[get_label(child)] = get_id(child)

    return result


def generate_variable_decl(instance, variable_decl, output_file):
    output_file.write(f"var<private> {ident_to_name(variable_decl)} : u32")
    pass


def generate_expression(instance, expr_identifier, output_file):
    output_file.write(f"0")
    pass


def generate_global_var_decl(instance, global_var_decl_identifier, output_file):
    print(global_var_decl_identifier)
    # Find associated variable decl
    global_decl_parent_id = get_id_from_ident("GlobalVarDecl")
    var_decl_field = get_field_from_instance(instance, label="variable_decl", parent_id=global_decl_parent_id)
    var_decl_tuples = find_tuples_by_key(var_decl_field, global_var_decl_identifier)

    assert len(var_decl_tuples) == 1

    generate_variable_decl(instance, var_decl_tuples[0][1], output_file)

    expr_field = get_field_from_instance(instance, label="expression", parent_id=global_decl_parent_id)
    expr_tuples = find_tuples_by_key(expr_field, global_var_decl_identifier)

    # If the variable is initialised with an expression
    if len(expr_tuples) == 1:
        output_file.write(" = ")
        generate_expression(instance, expr_tuples[0][1], output_file)

    output_file.write(";\n")


def generate_if_statement(instance, statement_identifier, output_file):
    output_file.write("  if (true) ")
    # TODO: Use compound statements for IfStatements
    generate_compound_statement(instance, statement_identifier, output_file)


def generate_while_statement(instance, statement_identifier, output_file):
    output_file.write("  while (true) ")
    generate_compound_statement(instance, statement_identifier, output_file)


def generate_statement(instance, statement_identifier, output_file):
    statement_type = ident_to_label(statement_identifier)
    match statement_type:
        case "WhileStatement":
            generate_while_statement(instance, statement_identifier, output_file)
        case "IfStatement":
            generate_if_statement(instance, statement_identifier, output_file)


def generate_compound_statement(instance, parent_identifier, output_file):
    output_file.write("{\n")
    parent_id = get_id_from_ident(parent_identifier)
    compound_statement_field = get_field_from_instance(instance, label="compound_statement", parent_id=parent_id)
    compound_statement_tuple = find_tuples_by_key(compound_statement_field, parent_identifier)

    assert len(compound_statement_tuple) == 1
    compound_statement_key = compound_statement_tuple[0][1]

    statements = get_field_from_instance(instance, label="statements", parent_id=get_id_from_ident("CompoundStatement"))
    statements_in_compound_statement = find_tuples_by_key(statements, compound_statement_key)

    for statement in statements_in_compound_statement:
        statement_identifier = statement[2]
        generate_statement(instance, statement_identifier, output_file)

    output_file.write("}\n")


def generate_function_decl(instance, function_decl_identifier, output_file):
    # Find the node ID for FunctionDecl
    function_decl_id = get_id_from_ident(function_decl_identifier)
    # Find the mapping from FunctionDecl to Ident
    function_ident_tuples = get_field_from_instance(instance,
                                                    label="ident",
                                                    parent_id=function_decl_id)
    function_ident_tuple = find_tuples_by_key(function_ident_tuples, function_decl_identifier)
    assert len(function_ident_tuple) == 1

    # Find the FunctionDecl's identifier
    function_ident = function_ident_tuple[0][1]

    output_file.write(f"\nfn {ident_to_name(function_ident)} () ")
    # Find associated compound statement
    generate_compound_statement(instance, function_decl_identifier, output_file)


def generate_global_decl(instance, global_decl_identifier, output_file):
    global_decl_type = ident_to_label(global_decl_identifier)
    match global_decl_type:
        case "GlobalVarDecl":
            generate_global_var_decl(instance, global_decl_identifier, output_file)
        case "FunctionDecl":
            generate_function_decl(instance, global_decl_identifier, output_file)


def generate_global_decls_for_translation_unit(instance, translation_unit, output_file):
    # Get the global declarations in the current translation unit.
    global_decl_tuples = get_global_decls_in_translation_unit(instance, translation_unit)

    for global_decl_tuple in global_decl_tuples:
        global_decl_identifier = global_decl_tuple[2]
        generate_global_decl(instance, global_decl_identifier, output_file)


def generate_program_from_instance(instance):
    translation_units = get_translation_units(instance)
    # Iterate over translation units
    for translation_unit in translation_units:
        translation_unit_file = open(get_label(translation_unit).replace('$', '') + ".wgsl", "w")

        generate_global_decls_for_translation_unit(instance, translation_unit, translation_unit_file)


def main():
    # Check the script is called correctly
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <xml_file>")
        sys.exit(1)

    # Read the provided xml file
    tree = elementTree.parse(sys.argv[1])

    # Check that the root node is an alloy node
    root = tree.getroot()
    assert root.tag == "alloy"

    instance = root[0]
    assert instance.tag == "instance"

    global label_to_id_dict
    label_to_id_dict = generate_label_to_id_dict(instance)
    generate_program_from_instance(instance)


if __name__ == '__main__':
    main()
