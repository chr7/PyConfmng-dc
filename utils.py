import re
import pytest
import pdb


def unindent(block, ignore_first_line=False):
    lines = str(block).split('\n')

    if ignore_first_line:
        del lines[0]

    for line in lines:
        if not line:
            # skip empty line
            continue
        # look at first non-empty line to see how much indentation to trim
        ws = re.match(r'\s*', line).group(0)
        break

    if ws:
        lines = list(map(lambda x: x.replace(ws, '', 1), lines))

    if lines[-1].isspace() or not lines[-1]:
        del lines[-1]
        final_eol = '\n'
    else:
        final_eol = ''

    return '\n'.join(lines) + final_eol


#---------------------------------------------------------------------------------------------------
testdata = [("""

        dictitems:
          current_settings: !!python/object/new:{0}.ConfVar
            dictitems:
              log: true
              log_file: my.log
              log_level: 5

          default_settings: !!python/object/new:{0}.ConfVar
            dictitems:
              log: false
              log_level: 1
    """, """

dictitems:
  current_settings: !!python/object/new:{0}.ConfVar
    dictitems:
      log: true
      log_file: my.log
      log_level: 5

  default_settings: !!python/object/new:{0}.ConfVar
    dictitems:
      log: false
      log_level: 1
""", False), ("""
        dictitems:
          log_level: 5""", """
dictitems:
  log_level: 5""", 0), (
      """
        dictitems:
          log_level: 5

      """,
"""
dictitems:
  log_level: 5

""", False),
    ("""
        log=True
        log_level=5
        log_file='my.log'
    """,
"""log=True
log_level=5
log_file='my.log'
"""
 , True),
    ("""
        log=True
         log_level=5
         log_file='my.log'
    """,
"""log=True
 log_level=5
 log_file='my.log'
"""
 , True)
]


#---------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("data_in, data_out, check_line", testdata)
def test_unindent_block(data_in, data_out, check_line):
    if check_line == 0:
        assert str(unindent(data_in)) == data_out
    else:
        assert str(unindent(data_in, check_line)) == data_out


#-- MAIN ------------------------------------------------------------------------------------------
if __name__ == "__main__":
    data_in = """
        log=True
        log_level=5
        log_file='my.log'
    """
    data_out= """log=True
log_level=5
log_file='my.log'
"""
    ret = unindent(data_in, True)
    assert str(data_out) == ret
