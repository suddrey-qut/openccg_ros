
import os
import subprocess
import rospkg

import xml.etree.ElementTree as ET

class OpenCCG:
  def __init__(self, grammar=None):
    rospack = rospkg.RosPack()
    pkg_path = rospack.get_path('openccg_ros')

    self.my_env = os.environ.copy()
    self.my_env['OPENCCG_HOME'] = os.path.join(pkg_path, 'openccg')
    self.my_env['PATH'] = '{}:{}'.format(self.my_env['PATH'], os.path.join(self.my_env['OPENCCG_HOME'], 'bin'))

    if 'JAVA_HOME' not in self.my_env:
      java_path = subprocess.check_output(['whereis', '-b', 'javac']).split()[1]
      self.my_env['JAVA_HOME'] = os.path.dirname(os.path.dirname(java_path))

    self.grammar = os.path.join(pkg_path, 'grammar/grammar.xml')
    self.process = None

  def __del__(self):
    if self.process:
      self.disconnect()

  def connect(self):
    self.process = subprocess.Popen(['bccg', self.grammar], stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=self.my_env)

  def disconnect(self):
    if self.process:
      self.process.terminate()
      self.process.wait()
      self.process = None

  def parse(self, text):
    if not self.process:
      raise Exception('OpenCCG.parse called before connect')
    self.process.stdin.write('{}\n'.format(text))
    result = self.process.stdout.readline()
    print(result)
    return [ET.fromstring(node.strip())
            for node in [child + '</xml>'
              for child in result.split('</xml>')[:-1]]]

  def __enter__(self):
    self.connect()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.disconnect()