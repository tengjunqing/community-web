/**
 * 本地存储工具函数
 */

/**
 * 获取存储项
 */
export function getStorage(key, defaultValue = null) {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : defaultValue
  } catch (error) {
    console.error('获取存储项失败:', error)
    return defaultValue
  }
}

/**
 * 设置存储项
 */
export function setStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.error('设置存储项失败:', error)
  }
}

/**
 * 移除存储项
 */
export function removeStorage(key) {
  try {
    localStorage.removeItem(key)
  } catch (error) {
    console.error('移除存储项失败:', error)
  }
}

/**
 * 清空所有存储
 */
export function clearStorage() {
  try {
    localStorage.clear()
  } catch (error) {
    console.error('清空存储失败:', error)
  }
}
