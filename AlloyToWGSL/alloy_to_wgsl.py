import sys
import xml.etree.ElementTree as elementTree


def get_sig_from_instance(instance, label: str):
    for child in instance:
        if child.tag == "sig" and child.attrib["label"].endswith(label):
            return child

    assert False  # This should never happen


def get_field_from_instance(instance, label: str):
    for child in instance:
        if child.tag == "field" and child.attrib["label"].endswith(label):
            return child

    assert False  # This should never happen


def get_atoms_from_sig(sig):
    result = set()
    for child in sig:
        if child.tag == "atom":
            result.add(child)

    return result


def find_tuple_by_key(instance, label: str):
    result = []
    for child in instance:
        if child.tag == "tuple" and child[0].tag == "atom" and child[0].attrib["label"].endswith(label):
            tuple = []
            for atom in child:
                tuple.append(atom.attrib["label"])
            result.append(tuple)

    return result


def main():
    # Check the script is called correctly
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <xml_file>")
        sys.exit(1)

    # Read the provided xml file
    tree = elementTree.parse(sys.argv[1])

    # Check that the root node has the correct format
    root = tree.getroot()
    assert root.tag == "alloy"
    # assert len(root) == 1

    instance = root[0]
    assert instance.tag == "instance"

    # - Iterate over each translation unit creating a new file for each
    # - For each translation unit, insert all associated global decls in order
    # TODO: Probably want to build a map from functions to names etc. before building a file.

    # Find the translation unit signature and get a list of all translation units
    translation_unit_sig = get_sig_from_instance(instance, "this/TranslationUnit")
    translation_units = get_atoms_from_sig(translation_unit_sig)

    # Iterate over translation units
    for translation_unit in translation_units:
        # TODO: Create new file for translation unit.
        translation_unit_file = open(translation_unit.attrib["label"].replace('$', '') + ".wgsl", "w")

        # Get the global decls for the current translation unit.
        global_decls_field = get_field_from_instance(instance, "global_decls")
        global_decl_tuples = find_tuple_by_key(global_decls_field, translation_unit.attrib["label"])

        # Find the name for each function
        for global_decl_tuple in global_decl_tuples:
            # Get function decl identifier
            function_decl = global_decl_tuple[2]
            ident_tuples = get_field_from_instance(instance, "ident")

            function_ident_tuple = find_tuple_by_key(ident_tuples, function_decl)
            assert len(function_ident_tuple) == 1

            function_ident = function_ident_tuple[0][1].replace('$', '')

            translation_unit_file.write(f"fn {function_ident} () {{\n")

            statements_field = get_field_from_instance(instance, "statements")
            print(function_decl)
            statements_tuples = find_tuple_by_key(statements_field, function_decl)
            print(statements_tuples)

            for statements_tuple in statements_tuples:
                if statements_tuple[2].startswith("IfStatement"):
                    translation_unit_file.write("  if (true) {}\n")


            translation_unit_file.write(f"}}\n\n")

        translation_unit_file.close()

if __name__ == '__main__':
    main()
