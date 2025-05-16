export default {
  async fetch(request, env, ctx) {
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const now = new Date();
    const dayKey = now.toISOString().slice(0, 10); // YYYY-MM-DD
    const weekKey = getWeekKey(now);               // YYYY-W##
    const monthKey = now.toISOString().slice(0, 7); // YYYY-MM

    // Ограничение: не более 10 визитов в день с одного IP
    const ipKey = `ip-${ip}-${dayKey}`;
    const ipVisits = parseInt(await env.VISITS_KV.get(ipKey) || "0");
    if (ipVisits >= 10) {
      return new Response("Too many visits", { status: 429 });
    }

    // Увеличиваем счётчики
    await Promise.all([
      env.VISITS_KV.put("total", `${(await getAndInc(env, "total"))}`),
      env.VISITS_KV.put(`day-${dayKey}`, `${(await getAndInc(env, `day-${dayKey}`))}`),
      env.VISITS_KV.put(`week-${weekKey}`, `${(await getAndInc(env, `week-${weekKey}`))}`),
      env.VISITS_KV.put(`month-${monthKey}`, `${(await getAndInc(env, `month-${monthKey}`))}`),
      env.VISITS_KV.put(ipKey, `${ipVisits + 1}`, { expirationTtl: 86400 })
    ]);

    // Вернём JSON статистику
    const result = {
      schemaVersion: 1,
      label: "Total Visits",
      message: await env.VISITS_KV.get("total"),
      color: "blueviolet"
    };

    return new Response(JSON.stringify(result), {
      headers: { "Content-Type": "application/json" }
    });
  }
}

async function getAndInc(env, key) {
  const value = parseInt(await env.VISITS_KV.get(key) || "0");
  return value + 1;
}

function getWeekKey(date) {
  const jan1 = new Date(date.getFullYear(), 0, 1);
  const days = Math.floor((date - jan1) / 86400000);
  const week = Math.ceil((days + jan1.getDay() + 1) / 7);
  return `${date.getFullYear()}-W${String(week).padStart(2, "0")}`;
}