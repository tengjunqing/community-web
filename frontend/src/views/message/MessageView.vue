<template>
  <div class="message-view">
    <div class="message-content">
      <!-- 会话列表 -->
      <div class="conversation-list">
        <div class="list-header">
          <h3>私信</h3>
        </div>

        <div class="list-content">
          <div
            v-for="conversation in conversations"
            :key="conversation.id"
            class="conversation-item"
            :class="{ active: currentConversation?.id === conversation.id }"
            @click="selectConversation(conversation)"
          >
            <UserAvatar :user="conversation.other_user" :size="48" />
            <div class="conversation-info">
              <div class="conversation-header">
                <span class="conversation-name">
                  {{ conversation.other_user?.nickname || conversation.other_user?.username }}
                </span>
                <span class="conversation-time">
                  {{ formatDateTime(conversation.last_message_at) }}
                </span>
              </div>
              <div class="conversation-preview">
                <span class="preview-text">
                  {{ conversation.last_message?.content || '暂无消息' }}
                </span>
                <el-badge
                  v-if="conversation.unread_count > 0"
                  :value="conversation.unread_count"
                  class="unread-badge"
                />
              </div>
            </div>
          </div>

          <el-empty v-if="conversations.length === 0" description="暂无会话" />
        </div>
      </div>

      <!-- 聊天窗口 -->
      <div class="chat-window">
        <template v-if="currentConversation">
          <div class="chat-header">
            <UserAvatar :user="currentConversation.other_user" :size="36" show-name />
          </div>

          <div class="chat-messages" ref="messagesContainer">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message-item"
              :class="{ 'message-self': message.sender_id === userStore.userId }"
            >
              <UserAvatar
                :user="message.sender_id === userStore.userId ? userStore.userInfo : currentConversation.other_user"
                :size="32"
              />
              <div class="message-content">
                <div class="message-bubble">{{ message.content }}</div>
                <div class="message-time">{{ formatDateTime(message.created_at) }}</div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="messageContent"
              placeholder="输入消息..."
              @keyup.enter="sendMessage"
            >
              <template #append>
                <el-button @click="sendMessage">发送</el-button>
              </template>
            </el-input>
          </div>
        </template>

        <div v-else class="chat-empty">
          <el-empty description="选择一个会话开始聊天" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { useMessageStore } from '@/stores/message'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { formatDateTime } from '@/utils/helpers'

const userStore = useUserStore()
const messageStore = useMessageStore()

const messagesContainer = ref(null)
const messageContent = ref('')

const conversations = computed(() => messageStore.conversations)
const currentConversation = computed(() => messageStore.currentConversation)
const messages = computed(() => messageStore.messages)

onMounted(async () => {
  await fetchConversations()
})

watch(currentConversation, async (conv) => {
  if (conv) {
    await fetchMessages(conv.id)
    await markAsRead(conv.id)
  }
})

async function fetchConversations() {
  try {
    await messageStore.fetchConversations()
  } catch (error) {
    console.error('获取会话列表失败:', error)
  }
}

async function fetchMessages(conversationId) {
  try {
    await messageStore.fetchMessages(conversationId, { skip: 0, limit: 50 })
    scrollToBottom()
  } catch (error) {
    console.error('获取消息列表失败:', error)
  }
}

async function markAsRead(conversationId) {
  try {
    await messageStore.markAsRead(conversationId)
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

function selectConversation(conversation) {
  messageStore.setCurrentConversation(conversation)
}

async function sendMessage() {
  if (!messageContent.value.trim() || !currentConversation.value) return

  try {
    await messageStore.sendMessage(currentConversation.value.id, {
      content: messageContent.value,
    })
    messageContent.value = ''
    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}
</script>

<style lang="scss" scoped>
.message-view {
  height: calc(100vh - 100px);
}

.message-content {
  display: flex;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.conversation-list {
  width: 320px;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;

  .list-header {
    padding: 16px;
    border-bottom: 1px solid #f0f0f0;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
  }

  .list-content {
    flex: 1;
    overflow-y: auto;
  }

  .conversation-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    cursor: pointer;
    transition: background 0.2s;

    &:hover {
      background: #f9f9f9;
    }

    &.active {
      background: #e8f4ff;
    }

    .conversation-info {
      flex: 1;
      min-width: 0;

      .conversation-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 4px;

        .conversation-name {
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }

        .conversation-time {
          font-size: 12px;
          color: #999;
        }
      }

      .conversation-preview {
        display: flex;
        align-items: center;
        justify-content: space-between;

        .preview-text {
          font-size: 13px;
          color: #666;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }
  }
}

.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;

  .chat-header {
    padding: 12px 16px;
    border-bottom: 1px solid #f0f0f0;
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;

    .message-item {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;

      &.message-self {
        flex-direction: row-reverse;

        .message-content {
          align-items: flex-end;
        }

        .message-bubble {
          background: #409eff;
          color: #fff;
        }
      }

      .message-content {
        display: flex;
        flex-direction: column;
        max-width: 70%;

        .message-bubble {
          padding: 8px 12px;
          background: #f0f0f0;
          border-radius: 8px;
          font-size: 14px;
          line-height: 1.5;
          word-break: break-word;
        }

        .message-time {
          font-size: 11px;
          color: #999;
          margin-top: 4px;
        }
      }
    }
  }

  .chat-input {
    padding: 12px 16px;
    border-top: 1px solid #f0f0f0;
  }

  .chat-empty {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
