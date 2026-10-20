from zk_chat.completion_defaults import ZK_CHAT_COMPLETION_CONFIG


class DescribeZkChatCompletionConfig:
    def should_request_a_context_window_large_enough_for_retrieved_notes(self):
        assert ZK_CHAT_COMPLETION_CONFIG.num_ctx == 32768

    def should_cap_generated_output(self):
        assert ZK_CHAT_COMPLETION_CONFIG.max_tokens == 16384

    def should_use_default_sampling_temperature(self):
        assert ZK_CHAT_COMPLETION_CONFIG.temperature == 1.0
