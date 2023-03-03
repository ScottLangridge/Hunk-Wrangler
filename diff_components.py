import re


class Diff:
    def __init__(self, text):
        self.full_text = [line.strip('\n') for line in text.splitlines()]
        self.files = []

    def parse(self):
        i = 1
        current_file = [self.full_text[0]]
        while i < len(self.full_text):
            if File.RE_FILE_NAME_HEADER.match(self.full_text[i]):
                self.files.append(File(current_file))
                current_file = []

            current_file.append(self.full_text[i])
            i += 1
        self.files.append(File(current_file))

        for file in self.files:
            file.parse()


class File:
    RE_FILE_NAME_HEADER = re.compile(r"diff --git a/(.*) b/(.*)")
    RE_SIMILARITY_HEADER = re.compile(r"similarity index (\d+)%")
    RE_NEW_FILE_HEADER = re.compile(r"new file mode (\d+)")
    RE_DELETED_FILE_HEADER = re.compile(r"deleted file mode (\d+)")
    RE_RENAME_FROM_HEADER = re.compile(r"rename from (.*)")
    RE_RENAME_TO_HEADER = re.compile(r"rename to (.*)")
    RE_INDEX_HEADER = re.compile(r"index ([0-9a-f]+)\.\.([0-9a-f]+)( [0-9]{6})?")
    RE_REMOVED_HEADER = re.compile(r"--- (a/(.*)|/dev/null)")
    RE_ADDED_HEADER = re.compile(r"\+\+\+ (b/(.*)|/dev/null)")
    RE_HUNK_START = re.compile(r"@@ -\d+,\d+ \+\d+,\d+ @@")

    def __init__(self, text):
        self.full_text = text

        self.new = False
        self.deleted = False
        self.renamed = False
        self.header_text = ""
        self.hunks = []

        self.first_hunk_line = None

    def parse_header(self):
        if self.full_text[1].startswith("index"):
            self.header_text = self.full_text[:4]
            assert self.RE_FILE_NAME_HEADER.match(self.header_text[0])
            assert self.RE_INDEX_HEADER.match(self.header_text[1])
            assert self.RE_REMOVED_HEADER.match(self.header_text[2])
            assert self.RE_ADDED_HEADER.match(self.header_text[3])
            self.first_hunk_line = 4

        elif self.full_text[1].startswith("similarity"):
            self.renamed = True

            if len(self.full_text) == 4:
                self.header_text = self.full_text[:4]
                self.first_hunk_line = None
                return

            self.header_text = self.full_text[:7]
            assert self.RE_FILE_NAME_HEADER.match(self.header_text[0])
            assert self.RE_SIMILARITY_HEADER.match(self.header_text[1])
            assert self.RE_RENAME_FROM_HEADER.match(self.header_text[2])
            assert self.RE_RENAME_TO_HEADER.match(self.header_text[3])
            assert self.RE_INDEX_HEADER.match(self.header_text[4])
            assert self.RE_REMOVED_HEADER.match(self.header_text[5])
            assert self.RE_ADDED_HEADER.match(self.header_text[6])
            self.first_hunk_line = 7

        elif self.full_text[1].startswith('new file'):
            self.new = True

            if len(self.full_text) == 3:
                self.header_text = self.full_text[:3]
                self.first_hunk_line = None
                return

            self.header_text = self.full_text[:5]
            assert self.RE_FILE_NAME_HEADER.match(self.header_text[0])
            assert self.RE_NEW_FILE_HEADER.match(self.header_text[1])
            assert self.RE_INDEX_HEADER.match(self.header_text[2])
            assert self.RE_REMOVED_HEADER.match(self.header_text[3])
            assert self.RE_ADDED_HEADER.match(self.header_text[4])
            self.first_hunk_line = 5

        elif self.full_text[1].startswith('deleted file'):
            self.deleted = True

            if len(self.full_text) == 3:
                self.header_text = self.full_text[:3]
                self.first_hunk_line = None
                return

            self.header_text = self.full_text[:5]
            assert self.RE_FILE_NAME_HEADER.match(self.header_text[0])
            assert self.RE_DELETED_FILE_HEADER.match(self.header_text[1])
            assert self.RE_INDEX_HEADER.match(self.header_text[2])
            assert self.RE_REMOVED_HEADER.match(self.header_text[3])
            assert self.RE_ADDED_HEADER.match(self.header_text[4])
            self.first_hunk_line = 5

        else:
            raise Exception("Unexpected header")

    def parse(self):
        self.parse_header()

        if self.first_hunk_line is None:
            return

        i = self.first_hunk_line
        current_hunk = [self.full_text[i]]
        while i + 1 < len(self.full_text):
            i += 1
            if self.RE_HUNK_START.match(self.full_text[i]):
                self.hunks.append(Hunk(current_hunk))
                current_hunk = []
            current_hunk.append(self.full_text[i])
        self.hunks.append(Hunk(current_hunk))

        for hunk in self.hunks:
            hunk.parse()


class Hunk:
    def __init__(self, hunk_text):
        self.full_text = hunk_text

        self.removed = []
        self.added = []

    def parse(self):
        for line in self.full_text:
            if line.startswith('-'):
                self.removed.append(line)
            elif line.startswith('+'):
                self.added.append(line)
