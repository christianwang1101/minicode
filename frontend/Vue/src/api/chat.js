export async function streamChat(message, mode = 'build', onEvent) {
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, mode })
  })

  if (!res.ok) {
    const text = await res.text()
    console.error('API error', res.status, text)
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value)
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
      if (!line.trim()) continue

      if (line.startsWith('data: ')) {
        const jsonStr = line.slice(6)
        try {
          const event = JSON.parse(jsonStr)
          onEvent(event)
        } catch (e) {
          console.warn('bad json:', jsonStr)
        }
      }
    }
  }

  if (buffer.trim().startsWith('data: ')) {
    const jsonStr = buffer.trim().slice(6)
    try {
      const event = JSON.parse(jsonStr)
      onEvent(event)
    } catch (e) {
      console.warn('final bad json:', jsonStr)
    }
  }
}
