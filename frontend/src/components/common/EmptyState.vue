<script setup lang="ts">defineProps<{title:string;text:string}>();</script><template><div class="empty"><span>⌁</span><h3>{{title}}</h3><p>{{text}}</p><slot/></div></template>
