import re

from diff_components import Diff


def main():
    SOURCE_DIFF_NAME = 'ss_whs_patch.patch'
    OUTPUT_DIFF_NAME = 'ss_pruned_diff.patch'

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

    print(
        f'{len(pruned_diff)}/{len(diff.full_text)} ({len(pruned_diff) / len(diff.full_text) * 100:.2f}% original size)')


def include_hunk(hunk):
    if len(hunk.removed) == len(hunk.added):
        changes = zip(hunk.removed, hunk.added)
        for change in changes:
            if include_change(*change):
                return True
        return False

    else:
        return True


def include_change(before, after):
    # Warehouse changed for workspace 1:1
    replacement_pairs = [['workspace', 'warehouse'], ['wks', 'whs']]
    for pair in replacement_pairs:
        if before.lower().strip("-+").replace(pair[0], pair[1]) == after.lower().strip("-+"):
            return False

    wks_url = re.compile(r"_(path|url)( |\()@?workspace")
    whs_url = re.compile(r"_(path|url)( |\()@?warehouse, @?workspace")
    if len(wks_url.findall(before)) == 1 and len(whs_url.findall(after)) == 1:
        return False

    return True


if __name__ == '__main__':
    main()
