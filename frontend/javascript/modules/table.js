/* global $ */
import DataTable from "datatables.net-bs5";

export default class Table {
  constructor(table) {
    this.table = new DataTable(table)
  }
}
