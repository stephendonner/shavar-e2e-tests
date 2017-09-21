import ConfigParser
import pytest
from foxpuppet import FoxPuppet
from selenium.webdriver import Firefox
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


from helper_prefs import set_prefs # noqa


@pytest.fixture()
def conf():
    config = ConfigParser.ConfigParser()
    config.read('prefs.ini')
    return config


"""
@pytest.fixture
def firefox_binary(firefox_binary):
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    return binary('.')

@pytest.fixture
def path_binary(foxpuppet):
    f = foxpuppet.selenium
    f.binary = '/Users/rpappalardo/git/ff-tool/.cache/browsers/FirefoxNightly.app/Contents/MacOS/firefox-bin'
    return f
"""


@pytest.fixture
def path_profile(foxpuppet):
    f = foxpuppet.selenium
    return '{0}/safebrowsing'.format(f.capabilities['moz:profile'])


def set_preferences(firefox_options, name_section):
    c = conf()
    defaults = c.items(name_section)
    print('\n====================================')
    print('PREF_SET SECTION: {0}'.format(name_section))
    print('====================================\n')
    for key, val in defaults:
        if val == 'true':
            val = True
        firefox_options.set_preference(key, val)
        print('KEY: {0}, VAL: {1}'.format(key, val))
    return firefox_options


@pytest.fixture
def firefox_options(firefox_options, pref_set):

    # TODO - path to binary
    #firefox_options.binary = '/Users/rpappalardo/git/ff-tool/.cache/browsers/FirefoxNightly.app/Content/MacOS/firefox' # noqa

    # 1. Set default conf values (loop through them)
    firefox_options = set_preferences(firefox_options, 'default')
    # 2. Set test env (stage or prod)
    firefox_options = set_preferences(firefox_options, 'stage')
    # This will come from: see - pytest_generate_tests
    firefox_options = set_preferences(firefox_options, pref_set)

    return firefox_options


@pytest.fixture
def browser(foxpuppet):
    """First Firefox browser window opened."""
    return foxpuppet.browser


@pytest.fixture
def foxpuppet(selenium, firefox_options):
    """Initialize the FoxPuppet object."""
    return FoxPuppet(selenium)


def pytest_addoption(parser):
    parser.addoption("--pref-set", action="append", default=[],
                     help="prefset to test")


def pytest_generate_tests(metafunc):
    c = conf()
    index = c.get('index', 'pref_sets_index')
    if index:
        index = index.split(',')

    pref_set = metafunc.config.getoption('pref_set')
    if pref_set:
        metafunc.parametrize('pref_set', pref_set)
    else:
        metafunc.parametrize('pref_set', index)
