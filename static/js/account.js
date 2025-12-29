document.addEventListener('alpine:init', () => {
  Alpine.data('personalDb', () => ({
    loading: false,

    create() {
      this.loading = true;
      fetch('/v1/db/create', { method: 'POST' }).then(location.reload.bind(location))
    },

    async refresh() {
      this.loading = true;
      if (confirm("Are you sure you want to refresh your database?"))
        await fetch('/v1/db/create?refresh=refresh', { method: 'POST' });
      this.loading = false;
    },

    async recreate() {
      this.loading = true;
      if (confirm("Are you sure you want to recreate your database?"))
        await fetch('/v1/db/create?refresh=refresh', { method: 'POST' });
      this.loading = false;
    }
  }))

  Alpine.data('apiKeys', () => ({
    keys: [],
    desc: '',
    newKey: null,

    init() {
      this.keys = window.serverApiKeys;
    },
    async deleteKey(evt) {
      const id = evt.target.closest('button').getAttribute('data-id');
      this.keys.splice(this.keys.findIndex(it => it.id == id), 1);
      await fetch(`/v1/auth/key?id=${id}`, { method: 'DELETE' });
    },
    async create() {
      const { key, id, description, createdOn } = await (await fetch(`/v1/auth/key?description=${encodeURIComponent(this.desc)}`)).json();
      this.newKey = key;
      this.keys.push({ id, description, createdOn });
      this.desc = '';
    }
  }))
})
