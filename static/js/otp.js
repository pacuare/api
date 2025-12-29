document.addEventListener('alpine:init', () => {
  Alpine.data('otpInput', () => ({
    value: '',
    isFocused: false,
    get digits() {
      return this.value.toUpperCase().padEnd(6).split('').slice(0, 6);
    },
    onInput(e) {
      this.value = e.target.value.slice(0, 6);
    }
  }))
})
