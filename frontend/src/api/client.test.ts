import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from './client'

describe('simulation API client', () => {
  afterEach(() => vi.unstubAllGlobals())
  it('requests current simulation state from the configured API', async () => {
    const payload = { step: 4, mode: 'hybrid' }
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(payload), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    await expect(api.state()).resolves.toEqual(payload)
    expect(fetchMock.mock.calls[0][0]).toContain('/simulation/state')
  })
})