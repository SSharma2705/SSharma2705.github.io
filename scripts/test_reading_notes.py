"""Checks for the Markdown input contract and generated journal navigation."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('journal', Path(__file__).with_name('build-reading-notes.py'))
journal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(journal)


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.entries = self.root / 'reading-notes' / 'entries'
        self.entries.mkdir(parents=True)

    def entry(self, text, filename='2026-11-06.md'):
        path = self.entries / filename
        path.write_text(text, encoding='utf-8')
        return path

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            journal.build(self.root)

    def test_source_dates_bullets_and_wrapping(self):
        day = journal.parse_day(self.entry('# My day\n\n## [A title](https://example.com/post)\n\nA source | updated 2026-11-04\n\n- First thought\n  continued here.\n\n* Second thought\n+ Third thought\n'))
        self.assertEqual(day['date'], '2026-11-06')
        self.assertEqual(day['title'], 'My day')
        note = day['notes'][0]
        self.assertEqual(note['source'], 'A source')
        self.assertEqual(note['source_date'], '2026-11-04')
        self.assertEqual(note['date_label'], 'updated')
        self.assertEqual(note['jottings'], ['First thought continued here.', 'Second thought', 'Third thought'])

    def test_missing_source_and_date_are_not_invented(self):
        day = journal.parse_day(self.entry('## [A](https://www.example.com/a)\n- Note\n'))
        note = day['notes'][0]
        self.assertEqual(note['source'], 'example.com')
        self.assertNotIn('source_date', note)
        self.assertIn('<p class="reading-source">example.com</p>', journal.render_day(day))

    def test_source_without_publication_date(self):
        note = journal.parse_day(self.entry('## [A](https://example.com/a)\nAn author\n- Note\n'))['notes'][0]
        self.assertEqual(note['source'], 'An author')
        self.assertNotIn('source_date', note)

    def test_title_anchors_and_existing_links(self):
        notes = journal.parse_day(self.entry('## [Repeated title](https://example.com/a) {#existing-link}\n- One\n## [Repeated title](https://example.com/b)\n- Two\n## [Repeated title](https://example.com/c)\n- Three\n'))['notes']
        self.assertEqual([n['id'] for n in notes], ['existing-link', 'repeated-title', 'repeated-title-2'])

    def test_invalid_input_reports_file_and_line(self):
        cases = [
            ('## [A](https://example.com)\n- Note\n  - Nested', '2026-11-06.md'),
            ('## [A](https://example.com)\n```python\nprint(1)\n```', '2026-11-06.md'),
            ('## Not a linked title\n- Note', '2026-11-06.md'),
            ('## [A](javascript:alert)\n- Note', '2026-11-06.md'),
            ('## [A](https://example.com)\nSource | 2026-02-30\n- Note', '2026-11-06.md'),
            ('## [A](https://example.com)\n', '2026-11-06.md'),
            ('## [A](https://example.com)\n- Note\nUnindented continuation', '2026-11-06.md'),
            ('## [A](https://example.com) {#same}\n- One\n## [B](https://example.com/b) {#same}\n- Two', '2026-11-06.md'),
        ]
        for content, filename in cases:
            with self.subTest(content=content):
                with self.assertRaisesRegex(ValueError, r'2026-11-06\.md:\d+:'):
                    journal.parse_day(self.entry(content, filename))

    def test_invalid_filename_date(self):
        with self.assertRaisesRegex(ValueError, 'valid date'):
            journal.parse_day(self.entry('## [A](https://example.com)\n- Note', '2026-02-30.md'))

    def test_inline_markdown_and_escaping(self):
        html = journal.inline_markdown('**bold** *italics* `a < b` [source](https://example.com/?a=1&b=2) <script>x</script>')
        self.assertIn('<strong>bold</strong>', html)
        self.assertIn('<em>italics</em>', html)
        self.assertIn('<code>a &lt; b</code>', html)
        self.assertIn('a=1&amp;b=2', html)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('href=', journal.inline_markdown('[unsafe](javascript:alert)'))

    def test_multiple_days_homepage_and_removing_an_entry(self):
        older = self.entry('## [Older](https://example.com/old)\n- Old note', '2026-11-05.md')
        newer = self.entry('# New day\n## [Newer](https://example.com/new)\n- New note')
        home = self.root / 'index.html'
        home.write_text('keep before <!-- research-journal-latest:start -->old<!-- research-journal-latest:end --> keep after')
        self.build()
        out = self.root / 'reading-notes'
        index = (out / 'index.html').read_text()
        self.assertLess(index.index('id="day-2026-11-06"'), index.index('id="day-2026-11-05"'))
        self.assertIn('2026-11-05.html">← Older entry', (out / '2026-11-06.html').read_text())
        self.assertIn('2026-11-06.html">Newer entry', (out / '2026-11-05.html').read_text())
        self.assertIn('New day →', home.read_text())
        self.assertIn('keep before', home.read_text())
        self.assertIn('keep after', home.read_text())
        first_build = {p.name: p.read_text() for p in out.glob('*.html')}
        self.build()
        self.assertEqual(first_build, {p.name: p.read_text() for p in out.glob('*.html')})
        (out / '2020-01-01.html').write_text('hand authored')
        newer.unlink()
        self.build()
        self.assertFalse((out / '2026-11-06.html').exists())
        self.assertTrue((out / '2020-01-01.html').exists())
        self.assertIn('2026-11-05.html', home.read_text())

    def test_invalid_entry_cannot_partially_overwrite_pages(self):
        self.entry('## [A](https://example.com)\n- Note', '2026-11-05.md')
        self.build()
        output = self.root / 'reading-notes' / 'index.html'
        previous = output.read_text()
        self.entry('## Broken heading\n- Note')
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(output.read_text(), previous)

    def test_bad_homepage_markers_fail_before_any_writes(self):
        self.entry('## [A](https://example.com)\n- Note')
        (self.root / 'index.html').write_text('missing markers')
        with self.assertRaisesRegex(ValueError, 'marker pair'):
            self.build()
        self.assertFalse((self.root / 'reading-notes' / 'index.html').exists())


if __name__ == '__main__':
    unittest.main()
