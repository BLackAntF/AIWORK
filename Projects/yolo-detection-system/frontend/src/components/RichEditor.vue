<template>
  <div class="rich-editor-wrapper">
    <editor-content :editor="editor" class="editor-content" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  },
  height: {
    type: Number,
    default: 400
  }
})

const emit = defineEmits(['update:modelValue'])

const editor = useEditor({
  content: props.modelValue || '',
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [1, 2, 3]
      }
    })
  ],
  editorProps: {
    attributes: {
      class: 'prose',
      style: `min-height: ${props.height}px; max-height: 600px; overflow-y: auto; padding: 16px;`
    }
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  }
})

watch(() => props.modelValue, (newVal) => {
  if (editor.value && newVal !== editor.value.getHTML()) {
    editor.value.commands.setContent(newVal || '', false)
  }
})

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<style scoped>
.rich-editor-wrapper {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--color-bg-primary);
}

.editor-content {
  width: 100%;
}

:deep(.ProseMirror) {
  outline: none;
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  font-size: 14px;
  line-height: 1.7;
}

:deep(.ProseMirror p) {
  margin: 0.5em 0;
}

:deep(.ProseMirror h1) {
  font-size: 1.8em;
  font-weight: 700;
  margin: 1em 0 0.5em;
}

:deep(.ProseMirror h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin: 0.8em 0 0.4em;
}

:deep(.ProseMirror h3) {
  font-size: 1.25em;
  font-weight: 600;
  margin: 0.6em 0 0.3em;
}

:deep(.ProseMirror ul),
:deep(.ProseMirror ol) {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

:deep(.ProseMirror li) {
  margin: 0.25em 0;
}

:deep(.ProseMirror blockquote) {
  border-left: 3px solid var(--color-accent);
  padding-left: 1em;
  margin: 1em 0;
  color: var(--color-text-secondary);
}

:deep(.ProseMirror code) {
  background: var(--color-bg-tertiary);
  padding: 0.1em 0.3em;
  border-radius: 3px;
  font-family: var(--font-family-mono);
  font-size: 0.9em;
}

:deep(.ProseMirror pre) {
  background: var(--color-bg-tertiary);
  padding: 1em;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 1em 0;
}

:deep(.ProseMirror pre code) {
  background: none;
  padding: 0;
}

:deep(.ProseMirror img) {
  max-width: 100%;
  border-radius: var(--radius-md);
}

:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  color: var(--color-text-tertiary);
  float: left;
  height: 0;
  pointer-events: none;
}
</style>
