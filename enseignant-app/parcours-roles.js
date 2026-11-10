'use strict';

window.EkoleRolesEnseignant = async (root, {make, json, isCurrent}) => {
 const data = await json('/api/parcours-roles.json');
 if (!isCurrent() || !data.themes.length) return;
 const section = make(root, 'section', 'b3-child-card');
 make(section, 'h3', '', 'Missions et questions reliées');
 make(section, 'p', '', 'Chaque rôle a un défi de pratique. Seules les questions relues de la banque deviennent accessibles dans ce rôle.');
 const details = make(section, 'details');
 make(details, 'summary', '', 'Voir les rôles et leurs questions');
 for (const theme of data.themes) {
  const group = make(details, 'details');
  make(group, 'summary', '', theme.name);
  const roles = make(group, 'ul');
  for (const role of theme.roles) {
   const row = make(roles, 'li');
   make(row, 'strong', '', role.name + ' · ' + role.title);
   make(row, 'p', '', role.course_title);
   for (const item of role.questions) {
    const label = item.id + ' · ' + (item.reviewed ? 'Relue' : 'À relire');
    const link = make(row, 'a', 'b3-secondary', label);
    link.href = '/?' + new URLSearchParams({banque_role: role.course, question_role: item.id});
    make(row, 'span', '', ' ');
   }
  }
 }
};
