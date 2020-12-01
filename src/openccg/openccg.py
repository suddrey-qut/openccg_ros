import os
import io
import rospy
import subprocess
import rospkg

from lxml import etree

class OpenCCG:
  def __init__(self, grammar=None):

    self.process = None

    rospack = rospkg.RosPack()
    pkg_path = rospack.get_path('openccg_ros')

    self.my_env = os.environ.copy()
    self.my_env['OPENCCG_HOME'] = os.path.join(pkg_path, 'openccg')
    self.my_env['PATH'] = '{}:{}'.format(self.my_env['PATH'], os.path.join(self.my_env['OPENCCG_HOME'], 'bin'))

    if 'JAVA_HOME' not in self.my_env:
      java_path = subprocess.check_output(['whereis', '-b', 'javac']).split()[1]
      self.my_env['JAVA_HOME'] = os.path.dirname(os.path.dirname(java_path))

    if not grammar:
      raise Exception('Missing parameter: grammar')
    
    self.grammar = grammar
    self.etree_parser = etree.XMLParser(remove_blank_text=True)

  def __del__(self):
    if self.process:
      self.disconnect()

  def connect(self):
    self.process = subprocess.Popen(['bccg', self.grammar], stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=self.my_env)
    rospy.loginfo('OpenCCG Connected')

  def disconnect(self):
    if self.process:
      self.process.terminate()
      self.process.wait()
      self.process = None

  def parse(self, text):
    if not self.process:
      raise Exception('OpenCCG.parse called before connect')
    
    self.process.stdin.write('{}\n'.format(text).encode(encoding='UTF-8'))
    self.process.stdin.flush()
    
    result = self.process.stdout.readline().decode('utf-8')
    
    return [etree.tostring(etree.XML(node.strip().encode(encoding='UTF-8'), parser=self.etree_parser)).decode('utf-8')
              for node in [child + '</xml>'
                for child in result.split('</xml>')[:-1]]]

  def __enter__(self):
    self.connect()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.disconnect()