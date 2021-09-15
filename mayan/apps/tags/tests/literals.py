from __future__ import unicode_literals

TEST_TAG_LABEL = 'test-tag'
TEST_TAG_LABEL_2 = 'test-tag-2'
TEST_TAG_LABEL_EDITED = 'test-tag-edited'
TEST_TAG_COLOR = '#001122'
TEST_TAG_COLOR_EDITED = '#221100'
TEST_TAG_INDEX_HAS_TAG = 'HAS_TAG'
TEST_TAG_INDEX_NO_TAG = 'NO_TAG'
TEST_TAG_INDEX_NODE_TEMPLATE = '''
{{% for tag in document.get_tags().all() %}}
    {{% if tag.label == "{label}" %}}
        {has_tag}
    {{% else %}}
        {not_tagged}
    {{% endif %}}
{{% else %}}
    {not_tagged}
{{% endfor %}}
'''.format(
    label=TEST_TAG_LABEL, has_tag=TEST_TAG_INDEX_HAS_TAG,
    not_tagged=TEST_TAG_INDEX_NO_TAG
).replace('\n', '')
