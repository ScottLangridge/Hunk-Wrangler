import re
from difflib import ndiff

from diff_components import Diff


def main():
    SOURCE_DIFF_NAME = 'my_patch.patch'
    OUTPUT_DIFF_NAME = 'pruned_diff.patch'

    with open("diffs/" + SOURCE_DIFF_NAME, 'r', encoding='utf-8') as f:
        patch_text = f.read()

    diff = Diff(patch_text)
    diff.parse()

    pruned_diff = []
    for file in diff.files:
        included_hunks = []
        for hunk in file.hunks:
            if include_hunk(hunk):
                included_hunks.append(hunk)

        if len(included_hunks) == 0:
            continue

        pruned_diff.extend(file.header_text)
        for hunk in included_hunks:
            pruned_diff.extend(hunk.full_text)

    str_pruned_diff = '\n'.join(pruned_diff)
    str_pruned_diff.rstrip()
    str_pruned_diff += '\n'

    with open("diffs/" + OUTPUT_DIFF_NAME, 'w', encoding='utf-8') as f:
        f.write(str_pruned_diff)

    print(f'{len(pruned_diff)}/{len(diff.full_text)} ({len(pruned_diff) / len(diff.full_text) * 100:.2f}% original size)')


def include_hunk(hunk):
    # Warehouse changed for workspace 1:1
    if len(hunk.removed) == 1 and len(hunk.added) == 1:
        char_diff = ndiff(hunk.removed[0].strip("-+ "), hunk.added[0].strip("-+ "))
        pruned_char_diff = filter(lambda i: not i.startswith(' '), char_diff)
        if ''.join(pruned_char_diff).replace('+ a+ r+ e+ h+ u- r- k- p- a- c', '') == '':
            return False

    # '_url(@workspace' --> '_url(@warehouse, @workspace'
    if len(hunk.removed) == 1 and len(hunk.added) == 1:
        wks_url = re.compile(r"_(path|url)( |\()@?workspace")
        whs_url = re.compile(r"_(path|url)( |\()@?warehouse, @?workspace")
        if len(wks_url.findall(hunk.removed[0])) == 1 and len(whs_url.findall(hunk.added[0])) == 1:
            return False

    return True


if __name__ == '__main__':
    main()
