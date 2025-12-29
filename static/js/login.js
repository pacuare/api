document.addEventListener('alpine:init', () => {
  Alpine.data('loginForm', () => ({
    otpVisible: false,
    error: false,
    email: '',

    async sendOtp(e) {
      e.preventDefault();
      const resp = await fetch('/v1/auth/verify?email=' + this.email);
      if (resp.status != 200) {
        this.error = true;
        return;
      }
      this.otpVisible = true;
    }
  }))
})
