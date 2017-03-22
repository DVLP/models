"""Tests for render_spec_with_graphviz."""





from tensorflow.python.platform import googletest
from dragnn.protos import spec_pb2
from dragnn.python import render_spec_with_graphviz
from dragnn.python import spec_builder


def _make_basic_master_spec():
  """Constructs a simple spec.

  Modified version of nlp/saft/opensource/dragnn/tools/parser_trainer.py

  Returns:
    spec_pb2.MasterSpec instance.
  """
  # Construct the "lookahead" ComponentSpec. This is a simple right-to-left RNN
  # sequence model, which encodes the context to the right of each token. It has
  # no loss except for the downstream components.
  lookahead = spec_builder.ComponentSpecBuilder('lookahead')
  lookahead.set_network_unit(
      name='FeedForwardNetwork', hidden_layer_sizes='256')
  lookahead.set_transition_system(name='shift-only', left_to_right='true')
  lookahead.add_fixed_feature(name='words', fml='input.word', embedding_dim=64)
  lookahead.add_rnn_link(embedding_dim=-1)

  # Construct the ComponentSpec for parsing.
  parser = spec_builder.ComponentSpecBuilder('parser')
  parser.set_network_unit(name='FeedForwardNetwork', hidden_layer_sizes='256')
  parser.set_transition_system(name='arc-standard')
  parser.add_token_link(source=lookahead, fml='input.focus', embedding_dim=32)

  master_spec = spec_pb2.MasterSpec()
  master_spec.component.extend([lookahead.spec, parser.spec])
  return master_spec


class RenderSpecWithGraphvizTest(googletest.TestCase):

  def test_constructs_simple_graph(self):
    master_spec = _make_basic_master_spec()
    contents = render_spec_with_graphviz.master_spec_graph(master_spec)
    self.assertIn('lookahead', contents)
    self.assertIn('<polygon', contents)
    self.assertIn('roboto, helvetica, arial', contents)
    self.assertIn('FeedForwardNetwork', contents)
    # Graphviz currently over-escapes hyphens.
    self.assertTrue(('arc-standard' in contents) or
                    ('arc&#45;standard' in contents))
    self.assertIn('input.focus', contents)
    self.assertTrue('input.word' not in contents,
                    "We don't yet show fixed features")


if __name__ == '__main__':
  googletest.main()
